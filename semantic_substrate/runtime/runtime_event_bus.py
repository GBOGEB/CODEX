from collections import deque
from datetime import datetime


class RuntimeEventBus:
    def __init__(self, max_events=100):
        self.events = deque(maxlen=max_events)

    def emit(self, source, event_type, payload):
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'source': source,
            'event_type': event_type,
            'payload': payload,
        }
        self.events.append(event)
        return event

    def latest(self, limit=10):
        return list(self.events)[-limit:]


if __name__ == '__main__':
    bus = RuntimeEventBus()
    bus.emit('replay_engine', 'reconstructed', {'snapshot': 'STATE-0001'})
    print(bus.latest())
