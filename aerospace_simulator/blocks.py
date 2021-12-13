from typing import Union, Optional, Callable


class Block:
    def __init__(self, name, simulation):
        self.name = name
        simulation.add(self)

    def finalise(self):
        pass

    def tick(self, dt):
        pass

    def value(self) -> Union[float, dict]:
        pass


class ConstantBlock(Block):
    def __init__(self, name, simulation, v: float):
        super().__init__(name, simulation)
        self._v = v

    def value(self) -> float:
        return self._v


class StepBlock(Block):
    _time_so_far = 0

    def __init__(self, name, simulation, value: float, on: float, off: Optional[float] = None, default_value: float = 0.0):
        super().__init__(name, simulation)
        self._value = value
        self._default_value = default_value
        self._on = on
        self._off = off

    def tick(self, dt):
        self._time_so_far += dt

    def value(self):
        if self._time_so_far >= self._on and (not self._off or self._time_so_far < self._off):
            return self._value
        else:
            return self._default_value


class UnaryFBlock(Block):
    def __init__(self, name, simulation, i: Block, f: Callable[[float], float]):
        super().__init__(name, simulation)
        self._f = f
        self._i = i

    def value(self):
        return self._f(self._i.value())


class BinaryFBlock(Block):
    def __init__(self, name, simulation, i1: Block, i2: Block, f: Callable[[float, float], float]):
        super().__init__(name, simulation)
        self._f = f
        self._i1 = i1
        self._i2 = i2

    def value(self):
        return self._f(self._i1.value(), self._i2.value())


class NaryFBlock(Block):
    def __init__(self, name, simulation, iarr: list[Block], f: Callable[[list[Block]], float]):
        super().__init__(name, simulation)
        self._f = f
        self._iarr = iarr

    def value(self):
        return self._f(self._iarr)


class IntegratingBlock(Block):
    def __init__(self, name, simulation, i: Block):
        super().__init__(name, simulation)
        self._v = 0
        self._i = i

    def tick(self, dt):
        self._v += dt * self._i.value()

    def value(self) -> float:
        return self._v


class LoopBlock(Block):
    def __init__(self, name, simulation, initial_value=0):
        super().__init__(name, simulation)
        self._i = None
        self._live = -1
        self._initial_value = initial_value

    def tick(self, dt):
        if not self._i:
            raise SystemError("Loop not initialized. Call set_input to set the variable to loop back!")
        self._live += 1

    def value(self):
        if self._live > 0:
            return self._i.value()
        else:
            return self._initial_value

    def set_input(self, i: Block):
        self._i = i


class Logger(Block):
    def __init__(self, name, simulation, i: Block, extractor: Callable[[dict], float]):
        super().__init__(name, simulation)
        self._i = i
        self._v = [extractor(i.value())]
        self._extractor = extractor

    def value(self) -> Union[float, dict]:
        return self._extractor(self._i.value())

    def tick(self, dt):
        self._v.append(self.value())

