from semantic_substrate.engines.tuple_registry_engine import TupleRegistryEngine


class TupleReplayEngine:
    def __init__(self):
        self.registry = TupleRegistryEngine()

    def replay(self, tuple_id):
        lineage = self.registry.lineage(tuple_id)

        return {
            'tuple_id': tuple_id,
            'lineage': lineage,
            'replay_depth': len(lineage),
            'root_reached': 'ROOT' in lineage,
        }


if __name__ == '__main__':
    engine = TupleReplayEngine()
    print(engine.replay('TUP-0001'))
