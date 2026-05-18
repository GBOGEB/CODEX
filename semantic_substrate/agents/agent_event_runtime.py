from datetime import datetime


def create_agent_event(agent_id, event_type, summary):
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'agent_id': agent_id,
        'event_type': event_type,
        'summary': summary,
    }


if __name__ == '__main__':
    print(
        create_agent_event(
            agent_id='AGENT-0002',
            event_type='runtime_update',
            summary='Implemented semantic replay engine',
        )
    )
