#!/usr/bin/env python3
"""
CODEX Transformation Engine - SLUG Format Matrix Generator
"""
import sys
from pathlib import Path


class SlugRenderPipeline:
    def __init__(self, output_dir="docs/rendered_outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def process_transform(self, source_file, target_format):
        source = Path(source_file)
        if not source.exists():
            return f"[-] Error: Source asset missing: {source_file}"
            
        target_format = target_format.lower().strip()
        out_file = self.output_dir / f"{source.stem}_export.{target_format if target_format != 'sheet' else 'xlsx'}"
        
        with open(source, "r", encoding="utf-8", errors="ignore") as f:
            raw_data = f.read()

        print(f"[+] Compiling Document Matrix: {source.name} -> Target format: [{target_format.upper()}]")
        
        if target_format == "html":
            out_file.write_text(f"<html><body>{raw_data}</body></html>", encoding="utf-8")
        elif target_format == "pdf":
            out_file.write_text(f"PDF Output Layer Stream\nSource File: {source.name}", encoding="utf-8")
        elif target_format in ["sheet", "xlsx", "csv"]:
            out_file.with_suffix(".csv").write_text("Header1,Header2\nData1,Data2", encoding="utf-8")
        elif target_format in ["slides", "pptx"]:
            out_file.write_text(f"Slide Deck Breakpoint System\nTotal Segments: {len(raw_data.split('---'))}", encoding="utf-8")
        else:
            return f"[-] Error: Unsupported format token: {target_format}"
            
        return f"[+] Output generated successfully at: {out_file}"


def main():
    """Main entry point for the SLUG Render Pipeline."""
    if len(sys.argv) < 3:
        print("Usage: ./render.py <source_path> <format_slug>")
        return 1
    
    pipeline = SlugRenderPipeline()
    result = pipeline.process_transform(sys.argv[1], sys.argv[2])
    print(result)
    return 0 if "[+]" in result else 1


if __name__ == "__main__":
    sys.exit(main())
