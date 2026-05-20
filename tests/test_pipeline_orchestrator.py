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
