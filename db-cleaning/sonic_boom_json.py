import sqlite3
import json
import logging
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import re

# Set up logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('theme_export.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ThemeExporter:
    def __init__(self, db_path: str, output_path: str = 'full_themes.json', 
                 indent: int = 0, batch_size: int = 1000, max_workers: int = 4):
        """
        Initialize the ThemeExporter with configuration options.
        
        Args:
            db_path: Path to the SQLite database
            output_path: Path for the output JSON file
            indent: JSON indentation (0 for compact, >0 for pretty)
            batch_size: Number of rows to process at a time
            max_workers: Maximum number of threads for parallel processing
        """
        self.db_path = db_path
        self.output_path = output_path
        self.indent = indent
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.conn = None
        self.cursor = None
        self.stats = {
            'total_rows': 0,
            'processed_rows': 0,
            'skipped_rows': 0,
            'error_rows': 0,
            'json_errors': 0,
            'start_time': None,
            'end_time': None,
            'categories': {},
            'stars_distribution': {'0': 0, '1-10': 0, '11-100': 0, '101-1000': 0, '1000+': 0}
        }
        
    def connect(self) -> None:
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def get_schema(self) -> List[str]:
        """Get and return the column names of the themes table."""
        try:
            self.cursor.execute("PRAGMA table_info(themes)")
            columns = [col[1] for col in self.cursor.fetchall()]
            logger.info(f"Columns in themes table: {columns}")
            return columns
        except sqlite3.Error as e:
            logger.error(f"Error getting schema: {e}")
            raise
    
    def create_backup(self) -> Optional[str]:
        """Create a backup of the database before processing."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.db_path}.backup_{timestamp}"
            
            # Create a backup connection
            backup_conn = sqlite3.connect(backup_path)
            
            # Backup the database
            with backup_conn:
                self.conn.backup(backup_conn)
            
            backup_conn.close()
            logger.info(f"Database backup created at: {backup_path}")
            return backup_path
        except sqlite3.Error as e:
            logger.warning(f"Failed to create backup: {e}")
            return None
    
    def get_total_rows(self) -> int:
        """Get the total number of rows in the themes table."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM themes")
            total = self.cursor.fetchone()[0]
            self.stats['total_rows'] = total
            logger.info(f"Total rows in themes table: {total}")
            return total
        except sqlite3.Error as e:
            logger.error(f"Error counting rows: {e}")
            return 0
    
    def process_row(self, row: Tuple, columns: List[str]) -> Optional[Dict[str, Any]]:
        """
        Process a single row from the database.
        
        Args:
            row: A tuple representing a row from the database
            columns: List of column names
            
        Returns:
            A dictionary representing the processed theme, or None if skipped
        """
        try:
            # Unpack row values with column names
            row_dict = dict(zip(columns, row))
            
            # Skip incomplete/error rows
            processing_status = row_dict.get('processing_status')
            if processing_status in ('error', 'pending', None):
                self.stats['skipped_rows'] += 1
                logger.debug(f"Skipped {row_dict.get('full_name', 'unknown')}: status '{processing_status}'")
                return None
            
            # Parse potentially JSON columns with error handling
            json_fields = ['files_str', 'images_str', 'stencil_patterns_str', 'tweaked_variants_str']
            parsed_fields = {}
            
            for field in json_fields:
                json_str = row_dict.get(field)
                try:
                    parsed_fields[field.replace('_str', '')] = json.loads(json_str) if json_str else []
                except (json.JSONDecodeError, TypeError) as e:
                    self.stats['json_errors'] += 1
                    logger.warning(f"Invalid JSON for {field} in {row_dict.get('full_name', 'unknown')}: {e}")
                    parsed_fields[field.replace('_str', '')] = []
            
            # Ensure types
            stars = int(row_dict.get('stars', 0)) if row_dict.get('stars') is not None else 0
            ui_mods_score = float(row_dict.get('ui_mods_score', 0)) if row_dict.get('ui_mods_score') is not None else 0.0
            
            # Update stars distribution
            if stars == 0:
                self.stats['stars_distribution']['0'] += 1
            elif 1 <= stars <= 10:
                self.stats['stars_distribution']['1-10'] += 1
            elif 11 <= stars <= 100:
                self.stats['stars_distribution']['11-100'] += 1
            elif 101 <= stars <= 1000:
                self.stats['stars_distribution']['101-1000'] += 1
            else:
                self.stats['stars_distribution']['1000+'] += 1
            
            # Update category count
            category = row_dict.get('category', 'unknown')
            self.stats['categories'][category] = self.stats['categories'].get(category, 0) + 1
            
            # Create theme object
            full_name = row_dict.get('full_name', '')
            theme_obj = {
                "full_name": full_name or "",
                "description": row_dict.get('description', '') or "",
                "stars": stars,
                "files": parsed_fields.get('files', []),
                "readme": row_dict.get('readme', '') or "",
                "images": parsed_fields.get('images', []),
                "category": category,
                "ai_description": row_dict.get('ai_description', '') or "",
                "ui_mods_score": ui_mods_score,
                "stencil_patterns": parsed_fields.get('stencil_patterns', []),
                "tweaked_variants": parsed_fields.get('tweaked_variants', []),
                "processing_status": processing_status or "unknown",
                # Add derived fields
                "github_url": f"https://github.com/{full_name}" if full_name else "",
                "repo_name": full_name.split('/')[-1] if full_name and '/' in full_name else "",
                "owner_name": full_name.split('/')[0] if full_name and '/' in full_name else "",
                "theme_id": hashlib.md5(full_name.encode()).hexdigest() if full_name else "",
                "has_images": len(parsed_fields.get('images', [])) > 0,
                "file_count": len(parsed_fields.get('files', [])),
                "has_readme": bool(row_dict.get('readme', '').strip()),
                "is_popular": stars > 100,
                "is_featured": ui_mods_score > 7.0,
                # Add timestamp
                "exported_at": datetime.now().isoformat()
            }
            
            # Extract keywords from description
            description = row_dict.get('description', '')
            if description:
                # Simple keyword extraction (could be enhanced with NLP)
                words = re.findall(r'\b\w+\b', description.lower())
                common_words = {'theme', 'themes', 'github', 'code', 'editor', 'syntax', 'color', 'colors'}
                keywords = [word for word in words if word not in common_words and len(word) > 3]
                theme_obj["keywords"] = keywords[:10]  # Limit to top 10 keywords
            
            self.stats['processed_rows'] += 1
            return theme_obj
            
        except Exception as e:
            self.stats['error_rows'] += 1
            logger.error(f"Error processing row: {e}")
            return None
    
    def process_batch(self, batch: List[Tuple], columns: List[str]) -> List[Dict[str, Any]]:
        """
        Process a batch of rows using parallel processing.
        
        Args:
            batch: List of row tuples
            columns: List of column names
            
        Returns:
            List of processed theme dictionaries
        """
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks to the executor
            future_to_row = {executor.submit(self.process_row, row, columns): row for row in batch}
            
            # Process completed tasks
            for future in as_completed(future_to_row):
                result = future.result()
                if result is not None:
                    results.append(result)
        
        return results
    
    def export_data(self) -> None:
        """Export data from the database to JSON file."""
        self.stats['start_time'] = time.time()
        
        try:
            # Get schema
            columns = self.get_schema()
            
            # Get total rows for progress tracking
            total_rows = self.get_total_rows()
            
            # Create backup
            backup_path = self.create_backup()
            
            # Process data in batches
            data = []
            offset = 0
            
            while offset < total_rows:
                # Fetch batch
                self.cursor.execute(f"SELECT * FROM themes LIMIT {self.batch_size} OFFSET {offset}")
                batch = self.cursor.fetchall()
                
                if not batch:
                    break
                
                # Process batch
                batch_results = self.process_batch(batch, columns)
                data.extend(batch_results)
                
                # Update progress
                processed = min(offset + self.batch_size, total_rows)
                progress = (processed / total_rows) * 100
                logger.info(f"Progress: {processed}/{total_rows} ({progress:.1f}%)")
                
                offset += self.batch_size
            
            # Write to file
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=self.indent, ensure_ascii=False)
            
            self.stats['end_time'] = time.time()
            self.log_stats()
            
            logger.info(f"Exported {len(data)} themes to {self.output_path}")
            
            # Create a summary file
            self.create_summary_file(data)
            
        except Exception as e:
            logger.error(f"Error during export: {e}")
            raise
        finally:
            self.close()
    
    def create_summary_file(self, data: List[Dict[str, Any]]) -> None:
        """Create a summary file with statistics about the exported data."""
        summary_path = os.path.splitext(self.output_path)[0] + '_summary.json'
        
        # Calculate additional statistics
        themes_with_images = sum(1 for theme in data if theme.get('has_images', False))
        themes_with_readme = sum(1 for theme in data if theme.get('has_readme', False))
        popular_themes = sum(1 for theme in data if theme.get('is_popular', False))
        featured_themes = sum(1 for theme in data if theme.get('is_featured', False))
        
        # Find top themes by stars
        top_themes = sorted(data, key=lambda x: x.get('stars', 0), reverse=True)[:10]
        
        summary = {
            "export_summary": {
                "export_date": datetime.now().isoformat(),
                "total_themes": len(data),
                "themes_with_images": themes_with_images,
                "themes_with_readme": themes_with_readme,
                "popular_themes": popular_themes,
                "featured_themes": featured_themes,
                "processing_time_seconds": round(self.stats['end_time'] - self.stats['start_time'], 2),
                "stars_distribution": self.stats['stars_distribution'],
                "categories": self.stats['categories'],
                "top_themes_by_stars": top_themes
            },
            "database_stats": self.stats
        }
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Summary file created at: {summary_path}")
    
    def log_stats(self) -> None:
        """Log processing statistics."""
        logger.info("=== Export Statistics ===")
        logger.info(f"Total rows in database: {self.stats['total_rows']}")
        logger.info(f"Rows processed: {self.stats['processed_rows']}")
        logger.info(f"Rows skipped: {self.stats['skipped_rows']}")
        logger.info(f"Rows with errors: {self.stats['error_rows']}")
        logger.info(f"JSON parsing errors: {self.stats['json_errors']}")
        logger.info(f"Processing time: {self.stats['end_time'] - self.stats['start_time']:.2f} seconds")
        logger.info("Stars distribution:")
        for range_name, count in self.stats['stars_distribution'].items():
            logger.info(f"  {range_name}: {count}")
        logger.info("Top categories:")
        sorted_categories = sorted(self.stats['categories'].items(), key=lambda x: x[1], reverse=True)[:10]
        for category, count in sorted_categories:
            logger.info(f"  {category}: {count}")
        logger.info("========================")
    
    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Export themes from SQLite to JSON')
    parser.add_argument('--db', default='raw_themes.db', help='Path to SQLite database')
    parser.add_argument('--output', default='full_themes.json', help='Output JSON file path')
    parser.add_argument('--indent', type=int, default=0, help='JSON indentation (0 for compact)')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for processing')
    parser.add_argument('--max-workers', type=int, default=4, help='Maximum number of threads')
    parser.add_argument('--backup', action='store_true', help='Create a backup of the database')
    
    args = parser.parse_args()
    
    # Create and run the exporter
    exporter = ThemeExporter(
        db_path=args.db,
        output_path=args.output,
        indent=args.indent,
        batch_size=args.batch_size,
        max_workers=args.max_workers
    )
    
    try:
        exporter.connect()
        exporter.export_data()
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
