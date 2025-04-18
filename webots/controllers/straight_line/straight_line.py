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

# Beweging instellen
vx = 0.2  # m/s
vy = 0.0
omega = 0.0

# Start de wielen met de gewenste snelheid
set_wheel_speeds(vx, vy, omega, kinematic)

# Functie om de robot een bepaalde afstand te laten rijden
def move_distance(target_distance, kinematic, tolerance=0.01):
    initial_pos = kinematic.getPos()
    target_x = initial_pos.x + target_distance
    
    while abs(initial_pos.x - target_x) > tolerance:
        kinematic.updateOdometry()
        set_wheel_speeds(vx, vy, omega, kinematic)  # Start de wielen
        robot.step(TIME_STEP)
        initial_pos = kinematic.getPos()  # Herbereken de positie

    # Stop de motoren na het bereiken van de afstand
    for i in range(4):
        wheels[i].setVelocity(0.0)

# Functie om de robot naar een bepaalde hoek te draaien
def turn_to_angle(current_angle, target_angle, kinematic, max_speed=1.0, tolerance=0.01):
    angle_diff = target_angle - current_angle
    while abs(angle_diff) > tolerance:
        if angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        elif angle_diff < -math.pi:
            angle_diff += 2 * math.pi

        # Bereken omega op basis van het verschil in hoeken
        omega = max_speed if angle_diff > 0 else -max_speed

        set_wheel_speeds(0.0, 0.0, omega, kinematic)  # Start de wielen voor draaien
        robot.step(TIME_STEP)
        current_angle += omega * (TIME_STEP / 1000.0)
        angle_diff = target_angle - current_angle

# Main loop: Beweeg de robot en draai naar een doelhoek
move_distance(1.0, kinematic)  # Beweeg 1 meter vooruit
turn_to_angle(0.0, math.pi / 2, kinematic)  # Draai naar 90 graden
move_distance(1.0, kinematic)  # Beweeg nogmaals 1 meter vooruit

# Stop de robot door snelheden op 0 te zetten
for i in range(4):
    wheels[i].setVelocity(0.0)

while robot.step(TIME_STEP) != -1:
    pass
