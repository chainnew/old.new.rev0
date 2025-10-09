import { NextRequest, NextResponse } from "next/server";
import * as fs from "fs/promises";
import * as path from "path";

interface FileToCreate {
  filename: string;
  content: string;
}

export async function POST(request: NextRequest) {
  try {
    const { files, baseDir } = await request.json() as { 
      files: FileToCreate[], 
      baseDir?: string 
    };

    if (!files || !Array.isArray(files) || files.length === 0) {
      return NextResponse.json({ error: "No files provided" }, { status: 400 });
    }

    const projectRoot = process.cwd();
    const targetDir = baseDir || projectRoot;
    const createdFiles: string[] = [];
    const errors: string[] = [];

    for (const file of files) {
      try {
        const fullPath = path.join(targetDir, file.filename);
        
        // Security check: prevent path traversal
        if (!fullPath.startsWith(targetDir)) {
          errors.push(`Security: Invalid path for ${file.filename}`);
          continue;
        }

        // Create directory if it doesn't exist
        const dir = path.dirname(fullPath);
        await fs.mkdir(dir, { recursive: true });

        // Write file
        await fs.writeFile(fullPath, file.content, 'utf-8');
        createdFiles.push(file.filename);
      } catch (error) {
        errors.push(`Failed to create ${file.filename}: ${error}`);
      }
    }

    return NextResponse.json({
      success: true,
      created: createdFiles,
      errors: errors.length > 0 ? errors : undefined,
      message: `Created ${createdFiles.length} file(s)`,
    });
  } catch (error) {
    console.error("File creation error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Failed to create files" },
      { status: 500 }
    );
  }
}
