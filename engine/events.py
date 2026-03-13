from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable


EventHandler = Callable[[dict[str, Any]], None]


@dataclass
class EventBus:
    _listeners: dict[str, list[EventHandler]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._listeners[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: EventHandler) -> None:
        if event_name in self._listeners:
            self._listeners[event_name] = [
                h for h in self._listeners[event_name] if h is not handler
            ]

    def emit(self, event_name: str, payload: dict[str, Any] | None = None) -> None:
        event_payload = payload or {}
       
        for handler in list(self._listeners.get(event_name, [])):
            handler(event_payload)

    def clear(self) -> None:
        self._listeners.clear()