from controller import Robot
from kinematic import RobotKinematic
import math

TIME_STEP = 32
robot = Robot()
kinematic = RobotKinematic.getInstance()

# === Setup motors ===
wheel_names = ["wheel1", "wheel2", "wheel3", "wheel4"]
wheels = []

for name in wheel_names:
    motor = robot.getDevice(name)
    motor.setPosition(float('inf'))  # Velocity control mode
    motor.setVelocity(0.0)
    wheels.append(motor)

# === Beweging instellen ===
vx = 2   # Vooruit in m/s
vy = 0.0   # Geen zijwaartse beweging
omega = 0.0  # Geen rotatie
ori = 0.0  # Oriëntatie voor inverse kinematics (gebruik bijv. IMU-data als die beschikbaar is)

# === Bereken de wielsnelheden met inverse kinematica ===
motion = kinematic.inversKinematic(vx, vy, omega, ori)
wheel_speeds = [motion.w1, motion.w2, motion.w3, motion.w4]

# === Pas snelheden toe op de motoren ===
for i in range(4):
    wheels[i].setVelocity(wheel_speeds[i])

# === Draai naar een bepaalde hoek ===
def turn_to_angle(current_angle, target_angle, kinematic, max_speed=1.0, tolerance=0.01):
    """
    Draait de robot naar de target_angle vanaf de current_angle.
    """
    angle_diff = target_angle - current_angle
    while abs(angle_diff) > tolerance:
        # Zorg ervoor dat de robot in de kortste richting draait
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        elif angle_diff < -math.pi:
            angle_diff += 2 * math.pi
        
        # Bereken omega op basis van het verschil in hoeken
        omega = max_speed if angle_diff > 0 else -max_speed

        # Bereken de wielsnelheden via inverse kinematica
        motion = kinematic.inversKinematic(0.0, 0.0, omega, current_angle)
        wheel_speeds = [motion.w1, motion.w2, motion.w3, motion.w4]

        # Pas snelheden toe op de motoren
        for i in range(4):
            wheels[i].setVelocity(wheel_speeds[i])

        robot.step(TIME_STEP)
        current_angle += omega * (TIME_STEP / 1000.0)  # Update de huidige hoek (voor iedere stap)
        angle_diff = target_angle - current_angle  # Herbereken het verschil

# === Beweging over een bepaalde afstand ===
def move_distance(distance, kinematic, speed=50.0, tolerance=0.01):
    """
    Beweegt de robot een bepaalde afstand vooruit.
    """
    initial_position = kinematic.getPos()
    target_position = initial_position.x + distance

    while abs(initial_position.x - target_position) > tolerance:
        motion = kinematic.inversKinematic(speed, 0.0, 0.0, initial_position.theta)
        wheel_speeds = [motion.w1, motion.w2, motion.w3, motion.w4]

        # Pas snelheden toe op de motoren
        for i in range(4):
            wheels[i].setVelocity(wheel_speeds[i])

        robot.step(TIME_STEP)
        initial_position = kinematic.getPos()  # Herbereken de positie

# === Main loop ===
current_angle = 0.0
turn_to_angle(current_angle, -math.pi / 2, kinematic)  # Draai naar 90 graden
move_distance(1.0, kinematic)  # Beweeg 5 meter vooruit

while robot.step(TIME_STEP) != -1:
    pass
