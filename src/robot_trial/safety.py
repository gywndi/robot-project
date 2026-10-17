"""Raw-tick limits, separate from transport and control. Not mechanical validation."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class JointLimits:
    max_offset_ticks: int
    max_step_ticks: int
    tolerance_ticks: int

    def __post_init__(self):
        for value in (self.max_offset_ticks, self.max_step_ticks, self.tolerance_ticks):
            if type(value) is not int:
                raise ValueError('Joint settings must be integer raw ticks')
        if not 0 < self.max_step_ticks <= self.max_offset_ticks:
            raise ValueError('Require 0 < max_step_ticks <= max_offset_ticks')
        if self.tolerance_ticks < 0:
            raise ValueError('Tolerance must be nonnegative')

    def check_target(self, anchor: int, target: int):
        if type(target) is not int or abs(target - anchor) > self.max_offset_ticks:
            raise ValueError('Target exceeds session-relative trial envelope')

    def check_step(self, anchor: int, current: int, target: int):
        self.check_target(anchor, current)
        self.check_target(anchor, target)
        if abs(target - current) > self.max_step_ticks:
            raise ValueError('Target exceeds single-step limit')


def positive_seconds(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError('Time must be finite and positive')
    return value
