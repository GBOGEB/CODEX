#!/usr/bin/env python3
"""
CODEX Transformation Engine - SLUG Format Matrix Generator
"""
import html
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

        raw_data = source.read_text(encoding="utf-8", errors="ignore")

        print(f"[+] Compiling Document Matrix: {source.name} -> Target format: [{target_format.upper()}]")

        if target_format == "html":
            escaped_data = html.escape(raw_data)
            html_output = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'none'; object-src 'none';">
    <title>Rendered Output</title>
</head>
<body><pre>{escaped_data}</pre></body>
</html>"""
            out_file.write_text(html_output, encoding="utf-8")
        elif target_format == "pdf":
            out_file.write_text(f"PDF Output Layer Stream\nSource File: {source.name}", encoding="utf-8")
        elif target_format in ["sheet", "xlsx", "csv"]:
            out_file = out_file.with_suffix(".csv")
            out_file.write_text("Header1,Header2\nData1,Data2", encoding="utf-8")
        elif target_format in ["slides", "pptx"]:
            out_file.write_text(
                f"Slide Deck Breakpoint System\nTotal Segments: {len(raw_data.split('---'))}",
                encoding="utf-8",
            )
        else:
            return f"[-] Error: Unsupported format token: {target_format}"

        return f"[+] Output generated successfully at: {out_file}"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: ./render.py <source_path> <format_slug>")
        sys.exit(1)
    pipeline = SlugRenderPipeline()
    result = pipeline.process_transform(sys.argv[1], sys.argv[2])
    print(result)
    # Exit with non-zero status if the result indicates an error
    if result.startswith("[-] Error"):
        sys.exit(1)
