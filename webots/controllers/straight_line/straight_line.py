from controller import Robot
from kinematic import RobotKinematic
import math

TIME_STEP = 32
robot = Robot()
kinematic = RobotKinematic.getInstance()

# Setup motors
wheels = []
for name in ["wheel1", "wheel2", "wheel3", "wheel4"]:
    motor = robot.getDevice(name)
    motor.setPosition(float('inf'))
    motor.setVelocity(0.0)
    wheels.append(motor)

# Functie om de wielen in te stellen op basis van inverse kinematica
def set_wheel_speeds(vx, vy, omega, kinematic):
    motion = kinematic.inversKinematic(vx, vy, omega)
    wheel_speeds = [motion.w1, motion.w2, motion.w3, motion.w4]
    for i in range(4):
        wheels[i].setVelocity(wheel_speeds[i])

def rijdt(richting_rad, afstand):
    snelheid = 0.2  # constante snelheid (m/s)
    vx = snelheid * math.cos(richting_rad)
    vy = snelheid * math.sin(richting_rad)
    omega = 0.0

    # Bepaal startpositie - MAAR maak een kopie!
    pos = kinematic.getPos()
    initial_pos = type(pos)(pos.x, pos.y, pos.theta)

    target_x = initial_pos.x + afstand * math.cos(richting_rad)
    target_y = initial_pos.y + afstand * math.sin(richting_rad)
    
    tolerance = 0.01  # 1 cm tolerantie

    while True:
        robot.step(TIME_STEP)
        kinematic.updateOdometry()
        current_pos = kinematic.getPos()

        dx = current_pos.x - initial_pos.x
        dy = current_pos.y - initial_pos.y
        distance_travelled = math.sqrt(dx**2 + dy**2)

        print(f"current_pos: {current_pos.x:.3f}, {current_pos.y:.3f}")
        print(f"initial_pos: {initial_pos.x:.3f}, {initial_pos.y:.3f}")
        print(f"distance_travelled: {distance_travelled:.3f}")

        if distance_travelled >= afstand - tolerance:
            break

        set_wheel_speeds(vx, vy, omega, kinematic)

    # Stop de motoren
    for i in range(4):
        wheels[i].setVelocity(0.0)

# --- Gebruik ---
rijdt(0, 1.0)            # 1 meter vooruit
rijdt(math.pi/2, 1.0)    # 1 meter naar links
rijdt(-math.pi/4, 1.0)   # 1 meter diagonaal rechtsvoor

# Blijf leven zonder iets te doen
while robot.step(TIME_STEP) != -1:
    pass