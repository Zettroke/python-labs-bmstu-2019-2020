##
# Медяновский Олег ИУ7-14Б
# Программа вычисляет корни функции на заданном интервале
# с определённым шагом разбиений методом хорд и выводит таблицу корней.
from threading import Thread
from typing import Tuple, Any, Callable, List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk, BOTH, Button, LEFT
from collections import namedtuple

Lin = namedtuple('Lin', 'k b')
Point = namedtuple('Point', 'x y')

STEP_MODE = False  # Пошаговое проигрывание анимации.
AUTOSTART = False  # Автоматическое начало/первый шаг анимации.
DELAY_MS = 50
X_CHANGE_REDRAW_COEF = 500  # 0.000000001  # 500

# Ввод данных
st, en = None, None
while True:
    try:
        st, en = map(float, input('Введите начало и конец отрезка: ').split())
        if en > st:
            break
        else:
            print('Конец должен быть больше начала!')
    except Exception:
        print('Ошибка ввода!')
div = None
while True:
    try:
        div = int(input('Введите кол-во разбиений: '))
        break
    except Exception:
        print('Ошибка ввода!')

eps = None
while True:
    try:
        eps = float(input('Введите точность eps: '))
        break
    except Exception:
        print('Ошибка ввода!')

ITER_LIMIT = 10_000  # Ограничение по числу итераций.
DELTA_THRESHOLD = (en - st) / X_CHANGE_REDRAW_COEF  # Изменение x при котором вызывается перерисовка.
lin_x = np.linspace(st, en, 400)  # Множество точек для построения графика.


# Целевая функция.
# def f(x):
#     return np.sin(x)


# Целевая функция.
def f(x):
    return 8*x**4-5*(x-0.1)+1


class App(Tk):
    done: bool = False
    st: float
    en: float
    div: int
    segment: int = 0
    # Фиксированная точка хорд.
    p_fixed: Point
    # Изменяемая точка хорды.
    p1: Point
    # Хорда
    hord: Lin = Lin(1, 0)
    iter_count: int = 0
    # Функция для которой мы ищем корни
    f: Callable[[Any], float]

    # Суммарное изменение x для отрисовки.
    delta_acc: float = 0
    # График
    ax: plt.Axes
    plots: List

    def __init__(self, st: float, en: float, div: int, f: Callable[[Any], float]):
        step = (en-st)/div
        super().__init__()
        self.st = st
        self.en = en
        self.div = div
        self.f = f
        self.next_segment(AUTOSTART)

        fig = plt.Figure(tight_layout=True)
        self.ax = fig.add_subplot()
        v = self.f(lin_x)
        self.ax.plot(lin_x, v, label='f(x)')
        self.plots = [
            self.ax.plot(lin_x, self.hord.k * lin_x + self.hord.b, label='lin')[0],
            self.ax.scatter([self.p1.x], [self.p1.y], marker='o', color='red'),
            self.ax.scatter([self.p_fixed.x], [self.p_fixed.y], marker='o', color='blue')
        ]
        mx_y = max(v)
        mn_y = min(v)
        m = (mx_y-mn_y)/50
        self.ax.set_ylim(mn_y-m, mx_y+m)

        for i in range(self.div+1):
            x = (st + step * i)
            self.ax.axvline(x, color='black')

        self.ax.axhline(0, color='black')

        self.fagg = FigureCanvasTkAgg(fig, self)
        self.fagg.get_tk_widget().pack(fill=BOTH, expand=1)
        self.fagg.draw()

        Button(self, text='start', command=self.next_step).pack()



    # Следующий шаг поиска корня.
    def next_step(self):
        if self.done:
            return
        try:
            while True:
                x1 = -self.hord.b / self.hord.k
                delta = abs(self.p1.x - x1)
                y1 = f(x1)
                if y1*self.p_fixed.y > 0:
                    self.p_fixed, self.p1 = self.p1, self.p_fixed
                self.p1 = Point(x1, y1)
                self.hord = self.points_to_hord(self.p1, self.p_fixed)
                self.delta_acc += delta
                self.iter_count += 1
                if delta < eps:
                    self.redraw()
                    break

                if self.iter_count > ITER_LIMIT:
                    step = (self.en - self.st) / self.div
                    x_s_st = self.st + step * (self.segment - 1)
                    x_s_en = self.st + step * self.segment
                    print('│{:^6}│{:^13.10}:{:^13.10}│{:^19.13}│{:^18.12}│{:^15}│{:^6}│'
                          .format(self.segment, x_s_st, x_s_en, '', '', self.iter_count, -2))
                    print("├──────┼───────────────────────────┼──────────"
                          "─────────┼──────────────────┼───────────────┼──────┤")
                    self.next_segment()
                    return

                if self.delta_acc > DELTA_THRESHOLD:
                    self.redraw()
                    self.delta_acc = 0
                    if not STEP_MODE and DELAY_MS != 0:
                        # Вызываю следующий шаг с аздержкой
                        self.after(DELAY_MS, self.next_step)
                    elif DELAY_MS == 0:
                        continue
                    return

            x1 = -self.hord.b / self.hord.k
            y1 = f(x1)
            step = (self.en - self.st) / self.div
            x_s_st = self.st + step * (self.segment - 1)
            x_s_en = self.st + step * self.segment
            print('│{:^6}│{:^13.10}:{:^13.10}│{:^19.13}│{:^18.12}│{:^15}│{:^6}│'
                  .format(self.segment, x_s_st, x_s_en, x1, y1, self.iter_count, ''))
            print("├──────┼───────────────────────────┼───────────────────┼──────────────────┼───────────────┼──────┤")

        except ZeroDivisionError:
            step = (self.en - self.st) / self.div
            x_s_st = self.st + step * (self.segment - 1)
            x_s_en = self.st + step * self.segment
            print('│{:^6}│{:^13.10}:{:^13.10}│{:^19.13}│{:^18.12}│{:^15}│{:^6}│'
                  .format(self.segment, x_s_st, x_s_en, '', '', self.iter_count, -1))
            print("├──────┼───────────────────────────┼───────────────────┼──────────────────┼───────────────┼──────┤")
        self.next_segment()

    # Перерисовка хорды и точек пересечения.
    def redraw(self):
        for pt in self.plots:
            pt.remove()
        self.plots = [
            self.ax.plot(lin_x, self.hord.k * lin_x + self.hord.b, label='lin', color='orange')[0],
            self.ax.scatter([self.p1.x], [self.p1.y], marker='o', color='red'),
            self.ax.scatter([self.p_fixed.x], [self.p_fixed.y], marker='o', color='blue')
        ]
        self.fagg.draw()
        self.ax.relim()

    # Переход к обработке следующего сегмента.
    def next_segment(self, start=True):
        self.segment += 1
        while self.segment <= self.div:
            self.iter_count = 0
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
                self.hord = self.points_to_hord(self.p1, self.p_fixed)

                if not STEP_MODE and start:
                    self.after(100, self.next_step)
                return

            self.segment += 1

        self.done = True
        print("Ошибка -1 : Деление на ноль")
        print("Ошибка -2 : Превышение максимального числа итераций")

    @staticmethod
    def points_to_hord(a: Tuple[float, float], b: Tuple[float, float]) -> Lin:
        if abs(b[0] - a[0]) < 1e-308:
            raise ZeroDivisionError()
        k = (b[1] - a[1]) / (b[0] - a[0])
        b = a[1] - k * a[0]
        return Lin(k, b)


print("┌──────┬───────────────────────────┬───────────────────┬──────────────────┬───────────────┬──────┐")
print("│# инт.│         Интервал          │       Корень      │  Значение ф-ции  │Кол-во итераций│Ошибка│")
print("├──────┼───────────────────────────┼───────────────────┼──────────────────┼───────────────┼──────┤")
app = App(st, en, div, f)
# if AUTOSTART:
#     app.after(50, app.next_segment)
# def ff():
#     if not AUTOSTART:
#         input('Нажмите ENTER для запуска!')
#         print('\r', end='')
#         app.after_idle(app.next_step)
# Thread(target=ff).start()

app.mainloop()
