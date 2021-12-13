from aerospace_simulator.simulation import Simulation
from aerospace_simulator.blocks import *
from aerospace_simulator.models import Aerial3DOF
from math import sin, cos, pi

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("WebAgg")


class PlottingLogger(Logger):
    def finalise(self):
        fig = plt.figure()
        fig.suptitle(self.name)
        plt.plot([i for i in range(0, len(self._v))], self._v)


# rocket params
engine_thrust = 15  # N
engine_burn_time = 30  # s
moment_arm = 0.3

# PID gains
gain_p = 0.02
gain_i = 0.01
gain_d = 0.05

max_gimbal_angle = 10 * pi / 180 # in radians

sim = Simulation()

gimbal_ang = LoopBlock('actuate', sim)

thrust = StepBlock('thrust', sim, engine_thrust, 0, engine_burn_time)
thrust_x_vector = BinaryFBlock('thrust-x', sim, thrust, gimbal_ang, lambda x, y: x * sin(-y))
thrust_z_vector = BinaryFBlock('thrust-z', sim, thrust, gimbal_ang, lambda x, y: x * cos(-y))

x_disturbance = StepBlock('disturbance', sim, 0.05, 6, 8)
total_x_vector = BinaryFBlock('+', sim, thrust_x_vector, x_disturbance, lambda x, y: x + y)

rotation_moment = UnaryFBlock('thrust moment', sim, total_x_vector, lambda x: x * moment_arm)

r = Aerial3DOF('rocket', sim, 0.5, 0.05, total_x_vector, thrust_z_vector, rotation_moment)

z_plot = PlottingLogger('rocket z position', sim, r, lambda v: v['z'])
x_plot = PlottingLogger('rocket x position', sim, r, lambda v: v['x'])

theta = PlottingLogger('theta', sim, r, lambda v: v['theta'])
rotation_speed = PlottingLogger('rotation_speed', sim, r, lambda v: v['q'])

integrated_theta = IntegratingBlock('i_theta', sim, theta)

P = UnaryFBlock('P', sim, theta, lambda x: x * gain_p)
I = UnaryFBlock('I', sim, integrated_theta, lambda x: x * gain_i)
D = UnaryFBlock('D', sim, rotation_speed, lambda x: x * gain_d)

pid = NaryFBlock('gimbal steering', sim, [P, I, D], lambda x: sum([n.value() for n in x]))
steering = UnaryFBlock('gimbal limited', sim, pid, lambda x: max(-max_gimbal_angle, min(x, max_gimbal_angle)))
gimbal_ang.set_input(steering)

steering_plot = PlottingLogger('steering', sim, steering, lambda v: v)

sim.simulate(lambda: r.value()['z'] < 0, 0.1)
plt.show()
