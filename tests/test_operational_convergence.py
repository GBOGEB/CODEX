from docs.wave_packages.runtime.ch15_solver_runtime import build_solver_report
from docs.wave_packages.runtime.covariance_execution_runtime import build_report as covariance_report
from docs.wave_packages.runtime.trust_arbitration_runtime import build_report as trust_report
from docs.wave_packages.runtime.runtime_dashboard_lockstep import validate as lockstep_validate
from docs.wave_packages.runtime.render_lockstep_runtime import validate_targets


def test_solver_runtime_convergence():
    report = build_solver_report()
    assert report['status'] == 'passed'
    assert report['validation']['density_positive'] is True


def test_covariance_runtime_convergence():
    report = covariance_report()
    assert 'covariance_matrix' in report
    assert report['uncertainty']['confidence_score'] >= 0


def test_trust_runtime_convergence():
    report = trust_report()
    assert 'confidence_score' in report
    assert isinstance(report['trust_zones'], list)


def test_dashboard_lockstep_runtime():
    report = lockstep_validate()
    assert 'parity_score' in report


def test_render_lockstep_runtime():
    report = validate_targets()
    assert 'render_parity_score' in report
