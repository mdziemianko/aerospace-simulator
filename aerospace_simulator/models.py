from .blocks import Block
from math import sin, cos, pi


class Aerial3DOF(Block):
    def __init__(self, name, simulation, mass, moi, Fx: Block, Fz: Block, My: Block, gravity=-9.81):
        super().__init__(name, simulation)
        self._mass = mass
        self._My = My
        self._Fx = Fx
        self._Fz = Fz
        self._iyy = moi
        self._gravity = gravity
        self._q = 0
        self._theta = 0
        self._w = 0
        self._u = 0
        self._x = 0
        self._z = 0
        self._Axe = 0
        self._Aze = 0
        self._dZe = 0
        self._dXe = 0

    def tick(self, dt):
        self._Axe = self._Fx.value() / self._mass - self._gravity * sin(self._theta)
        self._Aze = self._Fz.value() / self._mass + self._gravity * cos(self._theta)

        _du = self._Axe - self._q * self._w
        _dw = self._Aze + self._q * self._u

        _dq = self._My.value() / self._iyy
        self._q += _dq * dt
        self._theta += self._q * dt
        if self._theta < -2 * pi:
            self._theta += 2 * pi
        if self._theta > 2*pi:
            self._theta -= 2 * pi

        self._u += _du * dt
        self._w += _dw * dt

        self._z += self._dZe * dt + self._Aze * dt * dt / 2
        self._x += self._dXe * dt + self._Axe * dt * dt / 2

        self._dXe = self._u * cos(self._theta) + self._w * sin(self._theta)
        self._dZe = -self._u * sin(self._theta) + self._w * cos(self._theta)

    def value(self):
        return {'x': self._x, 'z': self._z,
                'a_x': self._Axe, 'a_z': self._Aze,
                'v_x': self._dXe, 'v_z': self._dZe,
                'theta': self._theta, 'q': self._q}
