/**
 * AssetPreview Component
 *
 * Renders various asset types inline:
 * - Markdown: Rendered with basic styling
 * - SVG: Displayed as images (sanitized)
 * - HTML: Rendered in a sandboxed iframe (no scripts)
 * - JSON: Formatted with syntax highlighting
 * - Images: Displayed as images (base64 or URL, validated)
 * - Text: Displayed as preformatted text
 * 
 * SECURITY NOTES:
 * - All content is sanitized via regex-based filtering (iterative application)
 * - SVG content has script tags, event handlers, and dangerous URLs removed
 * - HTML is rendered in an iframe with sandbox="" (most restrictive)
 * - Images are validated against allowed data URL prefixes
 * 
 * LIMITATIONS:
 * - Regex-based sanitization cannot catch all XSS vectors
 * - For untrusted external content, use a proper library like DOMPurify
 * - This implementation is suitable for internal artifact viewing from
 *   trusted sources (our own A2A agents)
 * 
 * @see https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html
 */

"use client";

import { useState, useMemo } from "react";

interface AssetPreviewProps {
  name: string;
  type: string;
  data: string;
  onClose?: () => void;
  maxHeight?: string;
}

/**
 * Sanitize SVG content by removing potentially dangerous elements and attributes.
 * Applies sanitization iteratively to handle nested/obfuscated attacks.
 * 
 * Note: For production use with untrusted content, consider using a proper
 * HTML sanitization library like DOMPurify. This implementation is for
 * internal artifact viewing where content comes from our own A2A agents.
 */
function sanitizeSvg(svg: string): string {
  let sanitized = svg;
  let previousLength: number;
  
  // Apply sanitization iteratively until no more changes
  // This handles nested patterns like <scr<script>ipt>
  do {
    previousLength = sanitized.length;
    
    // Remove script tags (multiple patterns for robustness)
    sanitized = sanitized.replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi, '');
    sanitized = sanitized.replace(/<script\b[^>]*\/>/gi, '');
    sanitized = sanitized.replace(/<script\b[^>]*>/gi, '');
    sanitized = sanitized.replace(/<\/script\s*>/gi, '');
    
    // Remove event handlers (onclick, onload, onerror, etc.)
    // Match on-* attributes with various quoting styles
    sanitized = sanitized.replace(/\s+on\w+\s*=\s*["'][^"']*["']/gi, '');
    sanitized = sanitized.replace(/\s+on\w+\s*=\s*[^\s>]+/gi, '');
    
    // Remove javascript:, vbscript:, and data: URLs (except safe image types)
    sanitized = sanitized.replace(/javascript\s*:/gi, '');
    sanitized = sanitized.replace(/vbscript\s*:/gi, '');
    sanitized = sanitized.replace(/data\s*:(?!image\/(png|jpg|jpeg|gif|svg\+xml|webp))[^"'\s>]*/gi, '');
    
    // Remove xlink:href and href with dangerous URLs
    sanitized = sanitized.replace(/xlink:href\s*=\s*["']\s*javascript:[^"']*["']/gi, '');
    sanitized = sanitized.replace(/href\s*=\s*["']\s*javascript:[^"']*["']/gi, '');
    
  } while (sanitized.length !== previousLength);
  
  return sanitized;
}

// Validate that a base64 string appears to be a valid image
function isValidImageData(data: string): boolean {
  // Check for valid data URL prefixes (strict checking)
  const validImagePrefixes = [
    'data:image/png;base64,',
    'data:image/jpeg;base64,',
    'data:image/jpg;base64,',
    'data:image/gif;base64,',
    'data:image/webp;base64,',
    'data:image/svg+xml;base64,',
  ];
  
  if (data.startsWith('data:')) {
    // Must match one of our allowed prefixes exactly
    return validImagePrefixes.some(prefix => data.toLowerCase().startsWith(prefix));
  }
  
  // Only allow http:// and https:// URLs (not data:, javascript:, vbscript:, etc.)
  if (data.startsWith('http://') || data.startsWith('https://')) {
    return true;
  }
  
  // For raw base64, validate it looks like base64
  const base64Regex = /^[A-Za-z0-9+/=]+$/;
  return base64Regex.test(data.replace(/\s/g, ''));
}

/**
 * Sanitize HTML for iframe display.
 * Applies sanitization iteratively to handle nested/obfuscated attacks.
 */
function sanitizeHtmlForIframe(html: string): string {
  let sanitized = html;
  let previousLength: number;
  
  // Apply sanitization iteratively
  do {
    previousLength = sanitized.length;
    
    // Remove script tags (multiple patterns for robustness)
    sanitized = sanitized.replace(/<script\b[^>]*>[\s\S]*?<\/script\s*>/gi, '');
    sanitized = sanitized.replace(/<script\b[^>]*\/>/gi, '');
    sanitized = sanitized.replace(/<script\b[^>]*>/gi, '');
    sanitized = sanitized.replace(/<\/script\s*>/gi, '');
    
    // Remove event handlers
    sanitized = sanitized.replace(/\s+on\w+\s*=\s*["'][^"']*["']/gi, '');
    sanitized = sanitized.replace(/\s+on\w+\s*=\s*[^\s>]+/gi, '');
    
    // Remove dangerous URLs
    sanitized = sanitized.replace(/javascript\s*:/gi, '');
    sanitized = sanitized.replace(/vbscript\s*:/gi, '');
    sanitized = sanitized.replace(/data\s*:(?!image\/(png|jpg|jpeg|gif|svg\+xml|webp))[^"'\s>]*/gi, '');
    
  } while (sanitized.length !== previousLength);
  
  return sanitized;
}

// Simple markdown renderer (basic support)
function renderMarkdown(markdown: string): string {
  const html = markdown
    // Escape HTML first for security
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    // Headers
    .replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold text-white mt-4 mb-2">$1</h3>')
    .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold text-white mt-6 mb-3">$1</h2>')
    .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold text-white mt-6 mb-4">$1</h1>')
    // Bold and italic
    .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-white">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="italic text-slate-300">$1</em>')
    .replace(/\_\_(.*?)\_\_/g, '<strong class="font-semibold text-white">$1</strong>')
    .replace(/\_(.*?)\_/g, '<em class="italic text-slate-300">$1</em>')
    // Code blocks
    .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="bg-slate-900 p-3 rounded-lg overflow-x-auto my-3"><code class="text-green-400 text-sm font-mono">$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code class="bg-slate-700 px-1.5 py-0.5 rounded text-purple-300 text-sm font-mono">$1</code>')
    // Lists
    .replace(/^\- (.*$)/gm, '<li class="text-slate-300 ml-4 list-disc">$1</li>')
    .replace(/^\* (.*$)/gm, '<li class="text-slate-300 ml-4 list-disc">$1</li>')
    .replace(/^\d+\. (.*$)/gm, '<li class="text-slate-300 ml-4 list-decimal">$1</li>')
    // Blockquotes
    .replace(/^&gt; (.*$)/gm, '<blockquote class="border-l-4 border-purple-500 pl-4 my-3 text-slate-400 italic">$1</blockquote>')
    // Links
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-purple-400 hover:underline">$1</a>')
    // Horizontal rules
    .replace(/^---$/gm, '<hr class="border-slate-700 my-4" />')
    // Paragraphs (double newlines)
    .replace(/\n\n/g, '</p><p class="text-slate-300 my-2">')
    // Single newlines to <br>
    .replace(/\n/g, '<br />');

  // Wrap in paragraph tags
  return `<p class="text-slate-300 my-2">${html}</p>`;
}

// Format JSON with syntax highlighting
function formatJson(json: string): string {
  try {
    const parsed = JSON.parse(json);
    const formatted = JSON.stringify(parsed, null, 2);
    return formatted
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      // Highlight strings
      .replace(/"([^"]+)":/g, '<span class="text-purple-400">"$1"</span>:')
      .replace(/: "([^"]*)"/g, ': <span class="text-green-400">"$1"</span>')
      // Highlight numbers
      .replace(/: (\d+)/g, ': <span class="text-yellow-400">$1</span>')
      // Highlight booleans
      .replace(/: (true|false)/g, ': <span class="text-blue-400">$1</span>')
      // Highlight null
      .replace(/: (null)/g, ': <span class="text-slate-500">$1</span>');
  } catch {
    return json;
  }
}

export default function AssetPreview({
  name,
  type,
  data,
  onClose,
  maxHeight = "500px",
}: AssetPreviewProps) {
  const [viewMode, setViewMode] = useState<"rendered" | "raw">("rendered");

  // Determine the asset type
  const assetType = useMemo(() => {
    const lowerType = type.toLowerCase();
    const lowerName = name.toLowerCase();

    if (lowerType.includes("svg") || lowerName.endsWith(".svg")) return "svg";
    if (lowerType.includes("markdown") || lowerType.includes("md") || lowerName.endsWith(".md")) return "markdown";
    if (lowerType.includes("html") || lowerName.endsWith(".html")) return "html";
    if (lowerType.includes("json") || lowerName.endsWith(".json")) return "json";
    if (lowerType.includes("image") || /\.(png|jpg|jpeg|gif|webp)$/i.test(lowerName)) return "image";
    if (lowerType.includes("text") || lowerType.includes("plain")) return "text";
    
    // Try to detect by content
    if (data.trim().startsWith("<svg")) return "svg";
    if (data.trim().startsWith("<!DOCTYPE html") || data.trim().startsWith("<html")) return "html";
    if (data.trim().startsWith("{") || data.trim().startsWith("[")) {
      try {
        JSON.parse(data);
        return "json";
      } catch {
        // Not valid JSON
      }
    }
    if (data.includes("# ") || data.includes("## ") || data.includes("**")) return "markdown";
    
    return "text";
  }, [type, name, data]);

  // Render the content based on type
  const renderedContent = useMemo(() => {
    if (viewMode === "raw") {
      return (
        <pre className="text-sm text-slate-300 font-mono whitespace-pre-wrap overflow-auto p-4">
          {data}
        </pre>
      );
    }

    switch (assetType) {
      case "svg":
        // Check if it's base64 encoded
        if (data.startsWith("data:image/svg+xml;base64,")) {
          // Validate base64 image data before rendering
          if (!isValidImageData(data)) {
            return (
              <div className="p-4 text-red-400">
                ⚠️ Invalid SVG data format
              </div>
            );
          }
          return (
            <div className="flex items-center justify-center p-4 bg-white rounded-lg">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={data} alt={name} className="max-w-full max-h-[400px]" />
            </div>
          );
        }
        // Render SVG directly with comprehensive sanitization
        return (
          <div 
            className="flex items-center justify-center p-4 bg-white rounded-lg"
            dangerouslySetInnerHTML={{ 
              __html: sanitizeSvg(data) 
            }} 
          />
        );

      case "markdown":
        return (
          <div 
            className="prose prose-invert max-w-none p-4 overflow-auto"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(data) }}
          />
        );

      case "html":
        // Render HTML in fully sandboxed iframe without scripts
        return (
          <iframe
            srcDoc={sanitizeHtmlForIframe(data)}
            title={name}
            className="w-full h-[400px] bg-white rounded-lg border border-slate-700"
            sandbox=""
          />
        );

      case "json":
        return (
          <pre 
            className="text-sm font-mono p-4 overflow-auto"
            dangerouslySetInnerHTML={{ __html: formatJson(data) }}
          />
        );

      case "image":
        // Validate image data before constructing URL
        let imgSrc: string;
        if (data.startsWith("data:") || data.startsWith("http://") || data.startsWith("https://")) {
          imgSrc = data;
        } else {
          // Assume raw base64, prepend with image/png data URL
          imgSrc = `data:image/png;base64,${data}`;
        }
        
        // Validate the constructed URL
        if (!isValidImageData(imgSrc)) {
          return (
            <div className="p-4 text-red-400">
              ⚠️ Invalid image data format
            </div>
          );
        }
        
        return (
          <div className="flex items-center justify-center p-4">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={imgSrc} alt={name} className="max-w-full max-h-[400px] rounded-lg" />
          </div>
        );

      case "text":
      default:
        return (
          <pre className="text-sm text-slate-300 font-mono whitespace-pre-wrap overflow-auto p-4">
            {data}
          </pre>
        );
    }
  }, [data, assetType, viewMode, name]);

  // Get icon for asset type
  const getTypeIcon = () => {
    switch (assetType) {
      case "svg": return "🖼️";
      case "markdown": return "📝";
      case "html": return "🌐";
      case "json": return "📋";
      case "image": return "🖼️";
      default: return "📄";
    }
  };

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-slate-700 flex items-center justify-between bg-slate-800/50">
        <div className="flex items-center gap-3">
          <span className="text-lg">{getTypeIcon()}</span>
          <div>
            <h4 className="font-medium text-white text-sm">{name}</h4>
            <span className="text-xs text-slate-500">{type} • {assetType}</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <div className="flex rounded-lg overflow-hidden border border-slate-600">
            <button
              onClick={() => setViewMode("rendered")}
              className={`px-3 py-1 text-xs transition ${
                viewMode === "rendered"
                  ? "bg-purple-500 text-white"
                  : "bg-slate-700 text-slate-400 hover:bg-slate-600"
              }`}
            >
              Rendered
            </button>
            <button
              onClick={() => setViewMode("raw")}
              className={`px-3 py-1 text-xs transition ${
                viewMode === "raw"
                  ? "bg-purple-500 text-white"
                  : "bg-slate-700 text-slate-400 hover:bg-slate-600"
              }`}
            >
              Raw
            </button>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="w-7 h-7 rounded-lg bg-slate-700 hover:bg-slate-600 text-slate-400 hover:text-white transition flex items-center justify-center"
            >
              ×
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div 
        className="overflow-auto bg-slate-900/50" 
        style={{ maxHeight }}
      >
        {renderedContent}
      </div>

      {/* Footer with size info */}
      <div className="px-4 py-2 border-t border-slate-700 bg-slate-800/30">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>{data.length.toLocaleString()} characters</span>
          <span>~{Math.ceil(data.length / 1024)} KB</span>
        </div>
      </div>
    </div>
  );
}
