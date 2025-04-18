import math

class Point2D:
    def __init__(self, x=0.0, y=0.0, theta=0.0):
        self.x = x
        self.y = y
        self.theta = theta

class Motion:
    def __init__(self):
        self.w1 = 0.0
        self.w2 = 0.0
        self.w3 = 0.0
        self.w4 = 0.0

class RobotKinematic:
    _instance = None

    @staticmethod
    def getInstance():
        if RobotKinematic._instance is None:
            RobotKinematic._instance = RobotKinematic()
        return RobotKinematic._instance

    def __init__(self):
        self.encData = [0.0] * 4
        self.prevEnc = [0.0] * 4
        self.Venc = [0.0] * 4
        self.pos = Point2D()
        self.vel = Point2D()

        self.a = 45  # hoek tussen wielen (graden)
        self.L = 20.8  # afstand tot wiel (cm)
        self.r_wheel = 6.0  # straal wiel (cm)
        self.circumference = 2 * math.pi * self.r_wheel

    def angleNormalize(self, angle):
        if angle > math.pi:
            angle -= 2 * math.pi
        if angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def setInitialPositon(self, x, y, theta):
        self.pos.x = x
        self.pos.y = y
        self.pos.theta = theta

    def getPos(self):
        return self.pos

    def ForwardKinematic(self, s1, s2, s3, s4):
        b = math.sqrt(2)
        out = Point2D()
        out.x = ((-b * s1) - (b * s2) + (b * s3) + (b * s4)) / 4
        out.y = ((b * s1) - (b * s2) - (b * s3) + (b * s4)) / 4
        out.theta = (s1 + s2 + s3 + s4) / (4 * self.L)
        return out

    def CalculateOdometry(self, ori):
        for i in range(4):
            tick = self.encData[i] - self.prevEnc[i]
            self.Venc[i] = tick * (self.circumference / (2 * math.pi))

        output = self.ForwardKinematic(*self.Venc)

        angleNorm = self.angleNormalize(self.pos.theta)
        self.pos.theta = angleNorm

        # Gebruik IMU-oriëntatie voor berekening
        velGlobal_x = math.cos(ori) * output.x - math.sin(ori) * output.y
        velGlobal_y = math.cos(ori) * output.y + math.sin(ori) * output.x

        self.pos.x += velGlobal_x / 100  # cm → m
        self.pos.y += velGlobal_y / 100
        self.pos.theta = ori

        self.prevEnc = list(self.encData)

    def inversKinematic(self, vx, vy, omega, ori):
        output = Motion()
        a_rad = math.radians(self.a)

        output.w1 = (-math.cos(a_rad) * vx + math.sin(a_rad) * vy + self.L * omega) / self.r_wheel
        output.w2 = (-math.cos(a_rad) * vx - math.sin(a_rad) * vy + self.L * omega) / self.r_wheel
        output.w3 = ( math.cos(a_rad) * vx - math.sin(a_rad) * vy + self.L * omega) / self.r_wheel
        output.w4 = ( math.cos(a_rad) * vx + math.sin(a_rad) * vy + self.L * omega) / self.r_wheel
        return output
