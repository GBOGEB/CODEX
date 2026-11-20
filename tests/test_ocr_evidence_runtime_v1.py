"""Generic source/raster fixtures; recognition quality is evaluated separately."""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import pytest

MODULE = Path(__file__).resolve().parents[1] / 'src/evidence/ocr_evidence_runtime_v1.py'
spec = importlib.util.spec_from_file_location('ocr_runtime_under_test', MODULE)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


def inputs(tmp_path):
    from pypdf import PdfWriter
    source = tmp_path / 'input.pdf'
    pdf = PdfWriter(); pdf.add_blank_page(width=300, height=200)
    pdf.write(source); pdf.close()
    raster = tmp_path / 'render.png'; raster.write_bytes(b'generic raster bytes')
    runtime = m.OCREvidenceRuntime()
    asset = runtime.asset_from_path(source)
    sidecar = runtime.decide_ocr(asset)
    options = dict(page_1based=1, raster_path=raster, text='Generic OCR result',
                   engine='test-executor', engine_version='1.2.3',
                   requested_languages=['eng'], available_languages=['eng', 'deu'],
                   model_sha256s={'eng': 'a' * 64}, parameters={'psm': 3, 'dpi': 200})
    return runtime, asset, sidecar, options


@pytest.mark.parametrize('confidence', [0.92, 0.999, 1.0])
def test_confidence_never_promotes_ocr_to_authority(confidence):
    runtime = m.OCREvidenceRuntime()
    sidecar = m.OCRSidecar('asset', m.OCRDecision.REQUIRED, confidence)
    assert runtime.may_promote_ocr(sidecar) is False


def test_decision_is_not_executed_evidence(tmp_path):
    r, a, s, _ = inputs(tmp_path)
    s.promoted_to_authoritative = True
    lineage = r.build_lineage(a, s)
    assert lineage.derived_artifacts == []
    assert lineage.sidecar.promoted_to_authoritative is False
    assert s.promoted_to_authoritative is True  # prior observation is immutable


def test_execution_binds_real_bytes_and_keeps_source_primary(tmp_path):
    r, a, s, opts = inputs(tmp_path)
    bound = r.record_execution(a, s, **opts)
    result = r.build_lineage(a, bound)
    assert result.evidence_primary and not result.sidecar.promoted_to_authoritative
    assert bound.execution['source_sha256'] == a.sha256
    assert result.derived_artifacts == ['ocr_sidecar']
    assert bound.execution['authority_effect'] == 'NONE'
    assert s.execution is None


def test_missing_language_fails_without_fallback(tmp_path):
    r, a, s, opts = inputs(tmp_path)
    opts['requested_languages'] = ['fra']
    with pytest.raises(ValueError, match='missing OCR languages: fra'):
        r.record_execution(a, s, **opts)


def test_model_digest_is_mandatory(tmp_path):
    r, a, s, opts = inputs(tmp_path)
    opts['model_sha256s'] = {}
    with pytest.raises(ValueError, match='exact model SHA256'):
        r.record_execution(a, s, **opts)


def test_changed_bytes_and_wrong_source_fail_closed(tmp_path):
    r, a, s, opts = inputs(tmp_path)
    s.asset_id = 'other'
    with pytest.raises(ValueError, match='another source'):
        r.build_lineage(a, s)
    with pytest.raises(ValueError, match='another source'):
        r.record_execution(a, s, **opts)
    s.asset_id = a.asset_id
    Path(a.path).write_bytes(b'changed source bytes')
    with pytest.raises(ValueError, match='source bytes'):
        r.record_execution(a, s, **opts)


def test_cache_changes_for_model_language_order_version_and_parameters(tmp_path):
    r, a, s, opts = inputs(tmp_path)
    baseline = r.record_execution(a, s, **opts).execution['cache_key_sha256']
    variants = [dict(engine_version='1.2.4'), dict(parameters={'psm': 6, 'dpi': 200}),
                dict(model_sha256s={'eng': 'b' * 64}),
                dict(requested_languages=['deu'], model_sha256s={'deu': 'a' * 64})]
    keys = [r.record_execution(a, s, **{**opts, **v}).execution['cache_key_sha256'] for v in variants]
    assert baseline not in keys and len(set(keys)) == 4
    both = {**opts, 'requested_languages': ['eng', 'deu'],
            'model_sha256s': {'eng': 'a' * 64, 'deu': 'b' * 64}}
    k1 = r.record_execution(a, s, **both).execution['cache_key_sha256']
    both['requested_languages'].reverse()
    assert r.record_execution(a, s, **both).execution['cache_key_sha256'] != k1


def test_nan_parameters_cannot_enter_deterministic_receipt(tmp_path):
    r, a, s, opts = inputs(tmp_path)
    opts['parameters'] = {'threshold': float('nan')}
    with pytest.raises(ValueError, match='finite JSON'):
        r.record_execution(a, s, **opts)


@pytest.mark.parametrize('page', [0, -1, True, '1'])
def test_bad_physical_page_rejected(tmp_path, page):
    r, a, s, opts = inputs(tmp_path)
    opts['page_1based'] = page
    with pytest.raises(ValueError, match='physical page'):
        r.record_execution(a, s, **opts)


@pytest.mark.parametrize('suffix', ['png', 'JPG', 'jpeg', 'tif', 'tiff', 'bmp', 'webp'])
def test_raster_extensions_are_images(tmp_path, suffix):
    path = tmp_path / ('raster.' + suffix); path.write_bytes(b'fixture')
    assert m.OCREvidenceRuntime.asset_from_path(path).source_format == m.EvidenceFormat.IMAGE


def test_skipped_or_deferred_work_does_not_create_an_execution(tmp_path):
    r, a, s, opts = inputs(tmp_path)
    for decision in (m.OCRDecision.SKIP, m.OCRDecision.DEFER_DWG_RENDER):
        s.decision = decision
        with pytest.raises(ValueError, match='does not permit'):
            r.record_execution(a, s, **opts)


def test_execution_cannot_be_rebound_to_different_asset(tmp_path):
    r, a, s, opts = inputs(tmp_path)
    bound = r.record_execution(a, s, **opts)
    a.sha256 = '0' * 64
    with pytest.raises(ValueError, match='source digest'):
        r.build_lineage(a, bound)


def test_lineage_detaches_execution_and_nested_parameters(tmp_path):
    r, a, s, opts = inputs(tmp_path)
    bound = r.record_execution(a, s, **opts)
    lineage = r.build_lineage(a, bound)
    bound.execution['page_1based'] = 999
    bound.execution['parameters']['psm'] = 99
    assert lineage.sidecar.execution['page_1based'] == 1
    assert lineage.sidecar.execution['parameters']['psm'] == 3


def test_auxiliary_model_changes_cache_key(tmp_path):
    r, a, s, opts = inputs(tmp_path)
    opts.update(engine='tesseract', parameters={'psm': 1},
                model_sha256s={'eng': 'a'*64, 'osd': 'b'*64})
    first = r.record_execution(a, s, **opts).execution['cache_key_sha256']
    opts['model_sha256s']['osd'] = 'c'*64
    assert r.record_execution(a, s, **opts).execution['cache_key_sha256'] != first
    del opts['model_sha256s']['osd']
    with pytest.raises(ValueError, match='osd'):
        r.record_execution(a, s, **opts)


@pytest.mark.parametrize('psm', ['1', 'auto_osd', True, -1, 14, None])
def test_psm_cannot_bypass_auxiliary_resource_gate(tmp_path, psm):
    r, a, s, opts = inputs(tmp_path)
    opts.update(engine='tesseract', parameters={'psm': psm})
    with pytest.raises(ValueError, match='explicit integer'):
        r.record_execution(a, s, **opts)


def test_relative_display_path_replays_against_resolved_source(tmp_path):
    r, a, s, opts = inputs(tmp_path)
    a = r.asset_from_path(Path(a.path), root=tmp_path)
    assert a.path == 'input.pdf'
    bound = r.record_execution(a, r.decide_ocr(a), **opts)
    assert bound.execution['source_sha256'] == a.sha256


def test_missing_pdf_page_is_rejected(tmp_path):
    r, a, s, opts = inputs(tmp_path)
    opts['page_1based'] = 2
    with pytest.raises(ValueError, match='physical PDF page'):
        r.record_execution(a, s, **opts)


@pytest.mark.parametrize('encrypted', [False, True])
def test_unreadable_or_encrypted_pdf_rejected(tmp_path, encrypted):
    from pypdf import PdfWriter
    r, a, s, opts = inputs(tmp_path)
    path = Path(a.path)
    if encrypted:
        pdf = PdfWriter(); pdf.add_blank_page(width=300, height=200)
        pdf.encrypt('synthetic-password'); pdf.write(path); pdf.close()
    else:
        path.write_bytes(b'not a PDF')
    a = r.asset_from_path(path)
    with pytest.raises(ValueError, match='source PDF|physical PDF'):
        r.record_execution(a, r.decide_ocr(a), **opts)


def test_incomplete_or_modified_receipt_is_not_executed_evidence(tmp_path):
    r, a, s, opts = inputs(tmp_path)
    s.execution = {'source_sha256': a.sha256}
    with pytest.raises(ValueError, match='incomplete'):
        r.build_lineage(a, s)
    bound = r.record_execution(a, s, **opts)
    bound.execution['parameters']['psm'] = 99
    with pytest.raises(ValueError, match='fingerprint mismatch'):
        r.build_lineage(a, bound)
    bound = r.record_execution(a, s, **opts)
    bound.execution['page_1based'] = 2
    with pytest.raises(ValueError, match='execution binding mismatch'):
        r.build_lineage(a, bound)


TSV_HEADER = 'level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext\n'
TSV_PAGE = '1\t1\t0\t0\t0\t0\t0\t0\t200\t200\t-1\t\n'


def test_actual_tsv_words_and_raw_confidence():
    text = TSV_HEADER + TSV_PAGE + '5\t1\t1\t1\t1\t1\t10\t20\t30\t40\t96.5\tExample\n'
    words = m.OCREvidenceRuntime.parse_tesseract_tsv(text)
    assert len(words) == 1 and words[0]['text'] == 'Example'
    assert words[0]['confidence_raw'] == 96.5


@pytest.mark.parametrize('text', ['', 'plain recognition text\n', 'unexpected\theader\n',
    TSV_HEADER + '5\t1\t1\t1\t1\t1\t10\t20\t30\t40\tnan\tExample\n',
    TSV_HEADER + '5\t1\t1\t1\t1\t1\t-10\t20\t30\t40\t95\tExample\n',
    TSV_HEADER + '5\t1\t1\n'])
def test_successful_exit_with_wrong_or_invalid_output_is_rejected(text):
    with pytest.raises(ValueError):
        m.OCREvidenceRuntime.parse_tesseract_tsv(text)


def test_valid_empty_page_is_distinct_from_malformed_output():
    assert m.OCREvidenceRuntime.parse_tesseract_tsv(TSV_HEADER + TSV_PAGE) == []


def test_out_of_bounds_word_rejected():
    text = TSV_HEADER + TSV_PAGE + '5\t1\t1\t1\t1\t1\t190\t20\t30\t40\t96.5\tExample\n'
    with pytest.raises(ValueError, match='outside its declared page'):
        m.OCREvidenceRuntime.parse_tesseract_tsv(text)


@pytest.mark.parametrize('text', [TSV_HEADER,
    TSV_HEADER+TSV_PAGE+'5\t1\t1\t1\t1\t1\t10\t20\t0\t40\t95\tExample\n',
    TSV_HEADER+TSV_PAGE+'5\t1\t1\t1\t1\t1\t10\t20\t30\t40\tnan\t\n'])
def test_truncated_and_empty_word_rows_still_validate(text):
    with pytest.raises(ValueError):
        m.OCREvidenceRuntime.parse_tesseract_tsv(text)
