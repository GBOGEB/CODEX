from src.pipeline.orchestrator import DeterministicPipelineOrchestrator


def test_pipeline_stage_order() -> None:
    orchestrator = DeterministicPipelineOrchestrator()
    result = orchestrator.run()

    assert result.status == 'completed'

    assert result.stages_executed == [
        'extract',
        'normalize',
        'validate',
        'render',
        'publish',
        'lineage',
    ]


def test_pipeline_reports_failed_stage() -> None:
    orchestrator = DeterministicPipelineOrchestrator()

    def _raise() -> None:
        raise RuntimeError('intentional failure')

    orchestrator.stages[2].handler = _raise
    result = orchestrator.run()

    assert result.status == 'failed'
    assert result.failed_stage == 'validate'
    assert result.error_message == 'intentional failure'
    assert result.stages_executed == ['extract', 'normalize']
