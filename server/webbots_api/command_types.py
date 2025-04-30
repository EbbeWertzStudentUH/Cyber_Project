from dataclasses import dataclass

@dataclass
class MovementCommand:
    distance: float
    angle: float

@dataclass
class PanicSignal:
    robot_id: str
    reason: str
    timestamp: str