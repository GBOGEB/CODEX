from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / 'semantic_substrate' / 'tuple_registry.yaml'


class TupleRegistryEngine:
    def __init__(self):
        self.registry = self._load_registry()

    def _load_registry(self):
        if not REGISTRY.exists():
            return {'tuples': []}
        with open(REGISTRY, 'r', encoding='utf-8') as handle:
            return yaml.safe_load(handle) or {'tuples': []}

    def get_tuple(self, tuple_id):
        for item in self.registry.get('tuples', []):
            if item.get('tuple_id') == tuple_id:
                return item
        return None

    def lineage(self, tuple_id):
        chain = []
        current = self.get_tuple(tuple_id)

        while current:
            chain.append(current.get('tuple_id'))
            parent = current.get('parent_id')
            if not parent:
                break
            current = self.get_tuple(parent)

        return chain


if __name__ == '__main__':
    engine = TupleRegistryEngine()
    print(engine.lineage('TUP-0001'))
