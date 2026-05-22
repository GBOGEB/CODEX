from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SemanticDocument:
    document_id: str
    title: str
    domain: str
    keywords: List[str] = field(default_factory=list)
    semantic_tags: List[str] = field(default_factory=list)


@dataclass
class QueryResult:
    document_id: str
    score: float
    matched_tags: List[str]


class SemanticRuntimeQueryEngine:
    """
    Wave 16 Semantic Runtime Query + Retrieval Engine.

    Purpose:
    - provide engineering semantic search
    - support evidence retrieval
    - enable cross-deck semantic indexing
    - establish runtime semantic retrieval infrastructure

    Platform:
    Engineering Deck Convergence Platform (EDCP)
    """

    def __init__(self):
        self.documents: Dict[str, SemanticDocument] = {}

    def register_document(self, document: SemanticDocument):
        self.documents[document.document_id] = document

    def semantic_query(self, query_tags: List[str]) -> List[QueryResult]:
        results = []

        for document in self.documents.values():
            matches = set(query_tags).intersection(document.semantic_tags)

            if matches:
                score = len(matches) / max(len(query_tags), 1)

                results.append(
                    QueryResult(
                        document_id=document.document_id,
                        score=round(score, 2),
                        matched_tags=sorted(matches),
                    )
                )

        return sorted(results, key=lambda r: r.score, reverse=True)

    def build_semantic_index(self) -> Dict:
        return {
            document_id: {
                "title": document.title,
                "domain": document.domain,
                "semantic_tags": document.semantic_tags,
            }
            for document_id, document in self.documents.items()
        }


if __name__ == "__main__":
    engine = SemanticRuntimeQueryEngine()

    engine.register_document(
        SemanticDocument(
            document_id="thermal_shields_001",
            title="Thermal Shields Reference Deck",
            domain="cryogenic",
            keywords=["thermal", "shield", "helium"],
            semantic_tags=["evidence", "topology", "cryogenic", "svg"],
        )
    )

    engine.register_document(
        SemanticDocument(
            document_id="manufacturing_001",
            title="Manufacturing QA Deck",
            domain="manufacturing",
            keywords=["quality", "inspection"],
            semantic_tags=["evidence", "inspection", "workflow"],
        )
    )

    results = engine.semantic_query(["evidence", "cryogenic"])
    semantic_index = engine.build_semantic_index()

    print(results)
    print(semantic_index)
