from datetime import datetime


class ReplayCheckpointRuntime:
    def create_checkpoint(self, snapshot_id, tuple_count, delta_count):
        return {
            'checkpoint_created_at': datetime.utcnow().isoformat(),
            'snapshot_id': snapshot_id,
            'tuple_count': tuple_count,
            'delta_count': delta_count,
            'checkpoint_status': 'created',
        }


if __name__ == '__main__':
    runtime = ReplayCheckpointRuntime()
    print(runtime.create_checkpoint('STATE-0001', 2, 1))
