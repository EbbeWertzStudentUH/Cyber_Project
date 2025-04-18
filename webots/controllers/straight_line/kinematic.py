import math

class Point2D:
    def __init__(self, x=0.0, y=0.0, theta=0.0):
        self.x = x
        self.y = y
        self.theta = theta

class Motion:
    def __init__(self, w1=0.0, w2=0.0, w3=0.0, w4=0.0):
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3
        self.w4 = w4

class RobotKinematic:
    _instance = None

    @staticmethod
    def getInstance():
        if RobotKinematic._instance is None:
            RobotKinematic._instance = RobotKinematic()
        return RobotKinematic._instance

    def __init__(self):
        self.pos = Point2D()
        self.r_wheel = 0.06  # m
        self.L = 0.208       # m
        self.a = math.radians(45)
        self.dt = 0.032      # 32ms (Webots TIME_STEP)
        self.last_motion = Motion()

    def updateOdometry(self):
        b = math.sqrt(2)
        m = self.last_motion

        # Wielsnelheden in m/s
        v1 = m.w1 * self.r_wheel
        v2 = m.w2 * self.r_wheel
        v3 = m.w3 * self.r_wheel
        v4 = m.w4 * self.r_wheel

        # Kinematica
        dx = ((-b * v1) - (b * v2) + (b * v3) + (b * v4)) / 4
        dy = ((b * v1) - (b * v2) - (b * v3) + (b * v4)) / 4
        dtheta = (v1 + v2 + v3 + v4) / (4 * self.L)

        # Update globale positie
        self.pos.x += math.cos(self.pos.theta) * dx * self.dt - math.sin(self.pos.theta) * dy * self.dt
        self.pos.y += math.sin(self.pos.theta) * dx * self.dt + math.cos(self.pos.theta) * dy * self.dt
        self.pos.theta += dtheta * self.dt

    def getPos(self):
        return self.pos

    def inversKinematic(self, vx, vy, omega):
        output = Motion()
        output.w1 = (-math.cos(self.a) * vx + math.sin(self.a) * vy + self.L * omega) / self.r_wheel
        output.w2 = (-math.cos(self.a) * vx - math.sin(self.a) * vy + self.L * omega) / self.r_wheel
        output.w3 = ( math.cos(self.a) * vx - math.sin(self.a) * vy + self.L * omega) / self.r_wheel
        output.w4 = ( math.cos(self.a) * vx + math.sin(self.a) * vy + self.L * omega) / self.r_wheel
        self.last_motion = output
        return output
