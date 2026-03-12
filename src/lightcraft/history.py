from __future__ import annotations

from dataclasses import dataclass, replace

from .models import EditState


@dataclass(slots=True)
class HistoryEntry:
    label: str
    state: EditState


class HistoryManager:
    def __init__(self, limit: int = 100) -> None:
        self._entries: list[HistoryEntry] = []
        self._index: int = -1
        self._limit = max(10, limit)

    @property
    def entries(self) -> list[HistoryEntry]:
        return list(self._entries)

    @property
    def index(self) -> int:
        return self._index

    def clear(self) -> None:
        self._entries.clear()
        self._index = -1

    def initialize(self, state: EditState, label: str) -> None:
        self._entries = [HistoryEntry(label=label, state=state.clone())]
        self._index = 0

    def capture(self, state: EditState, label: str) -> bool:
        if self._index >= 0 and self._entries[self._index].state == state:
            self._entries[self._index].label = label
            return False
        if self._index < len(self._entries) - 1:
            self._entries = self._entries[: self._index + 1]
        self._entries.append(HistoryEntry(label=label, state=state.clone()))
        if len(self._entries) > self._limit:
            overflow = len(self._entries) - self._limit
            self._entries = self._entries[overflow:]
            self._index = max(0, self._index - overflow)
        self._index = len(self._entries) - 1
        return True

    def can_undo(self) -> bool:
        return self._index > 0

    def can_redo(self) -> bool:
        return 0 <= self._index < len(self._entries) - 1

    def undo(self) -> EditState | None:
        if not self.can_undo():
            return None
        self._index -= 1
        return self.current_state()

    def redo(self) -> EditState | None:
        if not self.can_redo():
            return None
        self._index += 1
        return self.current_state()

    def jump_to(self, index: int) -> EditState | None:
        if index < 0 or index >= len(self._entries):
            return None
        self._index = index
        return self.current_state()

    def current_state(self) -> EditState | None:
        if self._index < 0 or self._index >= len(self._entries):
            return None
        return self._entries[self._index].state.clone()

    def current_label(self) -> str | None:
        if self._index < 0 or self._index >= len(self._entries):
            return None
        return self._entries[self._index].label

    def prune_future(self) -> None:
        if self._index < len(self._entries) - 1:
            self._entries = self._entries[: self._index + 1]
