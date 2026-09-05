class EventDispatcher:
    def __init__(self): self._handlers = {}
    def subscribe(self, event_type, handler): self._handlers.setdefault(event_type, []).append(handler)
    def dispatch(self, event_type, payload):
        return [handler(payload) for handler in self._handlers.get(event_type, [])]
