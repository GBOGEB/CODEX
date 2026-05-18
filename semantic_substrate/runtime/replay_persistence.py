from datetime import datetime


class ReplayPersistence:
    def persist_cycle(self, replay_state, drift_report, debt_report):
        return {
            'persisted_at': datetime.utcnow().isoformat(),
            'replay_state': replay_state,
            'drift_report': drift_report,
            'debt_report': debt_report,
            'persistence_status': 'captured',
        }


if __name__ == '__main__':
    persistence = ReplayPersistence()
    print(
        persistence.persist_cycle(
            replay_state={'snapshot': 'STATE-0001'},
            drift_report={'count': 0},
            debt_report={'score': 4},
        )
    )
