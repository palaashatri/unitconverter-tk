"""Runtime preferences and bounded conversion history."""

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class AppState:
    precision: int = 6
    use_scientific: bool = False
    history: list[str] = field(default_factory=list)
    dark_mode: bool = False
    on_change: Callable[[], None] | None = field(
        default=None, repr=False, compare=False
    )

    def add_history(self, entry: str) -> None:
        cleaned = str(entry).strip()
        if not cleaned:
            return
        self.history.insert(0, cleaned)
        del self.history[10:]
        if self.on_change is not None:
            self.on_change()
