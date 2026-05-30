"""
models/stage_model.py
Data container for a single stage's runtime state.
Controllers read/write this; Views read it.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class StageModel:
    stage_id:    str   = ""
    title:       str   = ""
    objective:   str   = ""           # shown to player
    duration:    float = 15.0         # max time allowed
    elapsed:     float = 0.0
    done:        bool  = False        # stage cleared
    failed:      bool  = False        # triggers game over
    fail_reason: str   = ""

    # generic bag for stage-specific data
    data: Dict[str, Any] = field(default_factory=dict)

    @property
    def remaining(self) -> float:
        return max(0.0, self.duration - self.elapsed)

    @property
    def progress(self) -> float:
        return min(1.0, self.elapsed / self.duration)

    def tick(self, dt: float):
        self.elapsed += dt
        if self.elapsed >= self.duration and not self.done:
            self.failed     = True
            self.fail_reason = "Time's up!"