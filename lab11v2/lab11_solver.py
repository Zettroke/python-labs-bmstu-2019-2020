from collections import namedtuple
from typing import Tuple, Callable

Lin = namedtuple('Lin', 'k b')
Point = namedtuple('Point', 'x y')
Solution = namedtuple('Solution', ['interval', 'x', 'y', 'iter', 'err'])


def points_to_hord(a: Tuple[float, float], b: Tuple[float, float]) -> Lin:
    if abs(b[0] - a[0]) < 1e-300:
        raise ZeroDivisionError()
    else:
        k = (b[1] - a[1]) / (b[0] - a[0])
    b = a[1] - k * a[0]
    return Lin(k, b)


class HordEquationSolver:
    st: float
    en: float
    eps: float
    div: int

    done: bool = False
    segment: int

    DELTA_THRESHOLD: float = 0.01
    ITER_LIMIT: int = 10000

    delta_acc: float = 0

    hord: Lin
    p_fixed: Point
    p1: Point

    iter_count: int
    err: int = 0

    f: Callable

    def __init__(self, st: float, en: float, div: int, eps: float, f: Callable):
        self.st, self.en, self.div, self.eps, self.f = st, en, div, eps, f

        self._setup()

    def _setup(self):
        self.segment = 0
        self.delta_acc = 0
        self.iter_count = 0
        self.err = 0
        self.p1 = Point(self.st, self.f(self.st))
        self.p_fixed = Point(self.en, self.f(self.en))
        self.hord = points_to_hord(self.p1, self.p_fixed)
        self.next_segment()

    def reset(self):
        self._setup()

    def next_step(self) -> bool:
        res = self._next_step()
        return res

    def _next_step(self) -> bool:
        while True:
            x1 = -self.hord.b / self.hord.k
            delta = abs(self.p1.x - x1)
            y1 = self.f(x1)
            if y1 * self.p_fixed.y > 0:
                self.p_fixed, self.p1 = self.p1, self.p_fixed
            self.p1 = Point(x1, y1)
            try:
                self.hord = points_to_hord(self.p1, self.p_fixed)
            except ZeroDivisionError:
                self.err = -1
                return True
            self.delta_acc += delta
            self.iter_count += 1
            if abs(y1) < self.eps:
                return True

            if self.iter_count > self.ITER_LIMIT:
                self.err = -2
                return True

            if self.delta_acc > self.DELTA_THRESHOLD:
                return False

    def next_segment(self) -> bool:
        self.segment += 1
        while self.segment <= self.div:
            self.iter_count = 0
            self.err = 0
            step = (self.en - self.st)/self.div
            x1 = self.st + step * (self.segment - 1)
            x2 = self.st + step * self.segment
            y1 = self.f(x1)
            y2 = self.f(x2)

            if y1*y2 <= 0:
                # Т.к. хорда вращается по часовой стрелке, то делаю так что бы она смотрела вниз.
                if y1 > y2:
                    x1, y1, x2, y2 = x2, y2, x1, y1
                self.p1 = Point(x1, self.f(x1))
                self.p_fixed = Point(x2, self.f(x2))
                self.hord = points_to_hord(self.p1, self.p_fixed)
                return False
            self.segment += 1
        self.done = True
        return True

    def get_current_segment(self):
        step = (self.en - self.st) / self.div
        return self.st + step * (self.segment - 1), self.st + step * self.segment

    def get_solution(self) -> Solution:
        return Solution(
            interval=self.get_current_segment(),
            x=self.p1.x,
            y=self.p1.y,
            iter=self.iter_count,
            err=self.err
        )
