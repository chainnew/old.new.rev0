/**
 * Sanitizes URLs to prevent XSS attacks in iframe src attributes
 * Based on OWASP recommendations
 */

const ALLOWED_PROTOCOLS = ['http:', 'https:', 'data:'];
const DANGEROUS_PROTOCOLS = ['javascript:', 'vbscript:', 'file:', 'about:'];

export function sanitizeUrl(url: string): string {
  if (!url || typeof url !== 'string') {
    return 'about:blank';
  }

  // Trim whitespace
  const trimmed = url.trim();
  
  // Empty or just whitespace
  if (!trimmed) {
    return 'about:blank';
  }

  try {
    // Try to parse as URL
    const parsed = new URL(trimmed, window.location.origin);
    
    // Check protocol
    if (DANGEROUS_PROTOCOLS.some(proto => parsed.protocol === proto)) {
      console.warn(`Blocked dangerous protocol: ${parsed.protocol}`);
      return 'about:blank';
    }

    // Only allow safe protocols
    if (!ALLOWED_PROTOCOLS.includes(parsed.protocol)) {
      console.warn(`Blocked unsupported protocol: ${parsed.protocol}`);
      return 'about:blank';
    }

    // Return sanitized URL
    return parsed.toString();
  } catch (error) {
    // If URL parsing fails, treat as relative URL
    // Check for dangerous patterns
    const lowerUrl = trimmed.toLowerCase();
    if (DANGEROUS_PROTOCOLS.some(proto => lowerUrl.startsWith(proto))) {
      console.warn(`Blocked dangerous URL pattern: ${trimmed}`);
      return 'about:blank';
    }

    // Return original if it's a safe relative URL
    return trimmed;
  }
}

/**
 * Validates if a URL is safe for iframe embedding
 */
export function isValidIframeUrl(url: string): boolean {
  if (!url || typeof url !== 'string') {
    return false;
  }

  try {
    const parsed = new URL(url, window.location.origin);
    return ALLOWED_PROTOCOLS.includes(parsed.protocol) && 
           !DANGEROUS_PROTOCOLS.includes(parsed.protocol);
  } catch {
    // Check for dangerous patterns in relative URLs
    const lowerUrl = url.toLowerCase().trim();
    return !DANGEROUS_PROTOCOLS.some(proto => lowerUrl.startsWith(proto));
  }
}
