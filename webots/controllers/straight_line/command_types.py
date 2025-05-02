from dataclasses import dataclass


# OUTGOING:
@dataclass
class MovementCommand:
    distance: float
    angle: float
    correct_centering: bool

@dataclass
class PickupCommand:
    product_id: str

@dataclass
class DropOffCommand:
    product_id: str

# INCOMING
@dataclass
class PanicResponse:
    robot_id: str
    reason: str
    timestamp: str

@dataclass
class MoveArriveResponse:
    robot_id: str
    success: bool
    driving_time: float

@dataclass
class PickupResponse:
    robot_id: str
    success: bool
    picking_time: float

@dataclass
class DropOffResponse:
    robot_id: str
    success: bool
    dropping_time: float