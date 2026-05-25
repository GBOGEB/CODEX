from pathlib import Path

from core_bridge.absorb import FederationBridgeEngine
from core_bridge.render import SlugRenderPipeline


def test_render_html_escapes_content(tmp_path: Path) -> None:
    source = tmp_path / "sample.txt"
    source.write_text("<script>alert('x')</script>\nline & two", encoding="utf-8")
    pipeline = SlugRenderPipeline(output_dir=tmp_path / "outputs")

    result = pipeline.process_transform(source, "html")

    assert str(tmp_path / "outputs" / "sample_export.html") in result
    html_output = (tmp_path / "outputs" / "sample_export.html").read_text(encoding="utf-8")
    assert "<pre>" in html_output
    assert "&lt;script&gt;alert(&#x27;x&#x27;)&lt;/script&gt;" in html_output
    assert "line &amp; two" in html_output


def test_render_sheet_token_outputs_csv(tmp_path: Path) -> None:
    source = tmp_path / "sample.txt"
    source.write_text("a,b\n1,2", encoding="utf-8")
    pipeline = SlugRenderPipeline(output_dir=tmp_path / "outputs")

    result = pipeline.process_transform(source, "sheet")

    out_path = tmp_path / "outputs" / "sample_export.csv"
    assert str(out_path) in result
    assert out_path.exists()
    assert out_path.read_text(encoding="utf-8") == "a,b\n1,2"


def test_absorb_patches_existing_index_idempotently(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "index.html").write_text(
        "<html><body><main class=\"surface-grid\"><div class=\"card-panel\"><h2>Base</h2></div></main></body></html>",
        encoding="utf-8",
    )
    (tmp_path / "GLOSSARY.yaml").write_text("terms:\n  - tag: A\n  - tag: B\n", encoding="utf-8")

    engine = FederationBridgeEngine(workspace_root=tmp_path)
    assert engine.execute_patch() is True
    assert engine.execute_patch() is True

    updated = (tmp_path / "docs" / "index.html").read_text(encoding="utf-8")
    assert updated.count('id="federation-bridge-status"') == 1
    assert "FEDERATION BRIDGE STATUS" in updated
