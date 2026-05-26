from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class PipelineStage:
    name: str
    description: str
    handler: Callable[[], None] | None = None


@dataclass
class PipelineRun:
    stages_executed: list[str] = field(default_factory=list)
    status: str = 'initialized'
    failed_stage: str | None = None
    error_message: str | None = None


class DeterministicPipelineOrchestrator:
    """Deterministic publication orchestration scaffold.

    Target lifecycle:

        extract
            -> normalize
            -> validate
            -> render
            -> publish
            -> lineage

    The orchestrator becomes the canonical execution spine for:
    - SSOT processing
    - renderer governance
    - validation
    - publication generation
    - lineage persistence
    """

    def __init__(self) -> None:
        self.stages = [
            PipelineStage('extract', 'source extraction and OCR'),
            PipelineStage('normalize', 'SSOT normalization'),
            PipelineStage('validate', 'governance and scientific validation'),
            PipelineStage('render', 'HTML/PDF/PPTX rendering'),
            PipelineStage('publish', 'artifact publication and GitHub Pages'),
            PipelineStage('lineage', 'manifest and traceability persistence'),
        ]

    def run(self) -> PipelineRun:
        result = PipelineRun(status='running')

        for stage in self.stages:
            try:
                if stage.handler:
                    stage.handler()
                result.stages_executed.append(stage.name)
            except Exception as exc:
                result.failed_stage = stage.name
                result.error_message = str(exc)
                result.status = 'failed'
                return result

        result.status = 'completed'
        return result


if __name__ == '__main__':
    orchestrator = DeterministicPipelineOrchestrator()
    result = orchestrator.run()

    print('pipeline execution order:')
    for stage in result.stages_executed:
        print(f' - {stage}')
