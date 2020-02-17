##
# Медяновский Олег ИУ7-14Б
# Программа вычисляет корни функции на заданном интервале
# с определённым шагом разбиений методом хорд и выводит таблицу корней.
import traceback
from tkinter.ttk import Treeview
from typing import Any, Callable, List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk, Button, Frame, Entry, Label, StringVar, DoubleVar, IntVar, Scale, HORIZONTAL
from collections import namedtuple

from matplotlib.lines import Line2D

from lab11v2.lab11_solver import HordEquationSolver

Lin = namedtuple('Lin', 'k b')
Point = namedtuple('Point', 'x y')

DELAY_MS = 50
X_CHANGE_REDRAW_COEF = 500  # 0.000000001  # 500

# g_st, g_en = 0, 1
g_st, g_en = -10, 10
g_eps = 0.00000001
g_div = 9
ITER_LIMIT = 10_000  # Ограничение по числу итераций.
DELTA_THRESHOLD = (g_en - g_st) / X_CHANGE_REDRAW_COEF  # Изменение x при котором вызывается перерисовка.
# DEFAULT_EXPRESSION = '8*x**4-5*(x-0.1)+1'
DEFAULT_EXPRESSION = 'np.sin(x)'


# Класс оборачивающий метод и следящий за тем что бы внутренний метод не вызывался чаще через t миллисекунд
class Debouncer:
    t: int
    func: Callable
    tk: Tk
    last_job_id: any = None

    def __init__(self, tk, func, t):
        self.tk = tk
        self.func = func
        self.t = t

    def __call__(self, *args, **kwargs):
        if self.last_job_id:
            self.tk.after_cancel(self.last_job_id)
        else:
            self.func(*args)
        self.last_job_id = self.tk.after(self.t, self.func, *args)


class App(Tk):
    STEP_MODE = False  # Пошаговое проигрывание анимации.

    started = False  # Мы начали искать корни, в это время нельзя менять менять уравнение.
    paused = False
    done: bool = False
    st: float
    en: float
    div: int
    eps: float

    lin_x: any  # Множество точек для построения графика.
    lin_space_size: int = 400

    solver: HordEquationSolver

    f: Callable[[Any], float]

    # График
    ax: plt.Axes
    plots: List[Line2D] = []
    h_lines: List[Line2D] = []
    main_plot: any = None

    solutions: List = []

    tree: Treeview
    b_start: Button

    cached_function: any

    def f(self, x):
        return self.cached_function(x)

    def __init__(self, st: float, en: float, div: int, eps: float):
        step = (en-st)/div
        super().__init__()
        self.st = st
        self.en = en
        self.div = div
        self.eps = eps
        self.lin_x = np.linspace(st, en, self.lin_space_size)  # Множество точек для построения графика.

        fig = plt.Figure(tight_layout=True)
        self.ax = fig.add_subplot()

        self.ax.axhline(0, color='black')

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.fagg = FigureCanvasTkAgg(fig, self)
        self.fagg.get_tk_widget().grid(row=0, column=0, sticky='WNSE')
        self.frame = Frame(self, background='green')
        self.frame.grid(row=0, column=1, sticky='WNSE', rowspan=2)

        self.init_sidebar()

        self.solver = HordEquationSolver(st, en, div, eps, self.f)

        self.prepare()

        # self.fagg.get_tk_widget().pack(fill=BOTH, expand=1)
        self.fagg.draw()
        button_frame = Frame(self, bg='blue')
        button_frame.grid(row=1, column=0, sticky='WE')
        self.b_start = Button(button_frame, text='start')
        self.b_start.pack(side='left', anchor='center')
        self.b_start.bind('<Button>', self.start)
        Button(button_frame, text='reset', command=self.reset).pack(side='left', anchor='center')

        # Button(self, text='12312123').pack(side=LEFT)

    def init_sidebar(self):
        self.cached_function = eval('lambda x: ' + DEFAULT_EXPRESSION)
        self.expr = StringVar(self)
        self.expr.set(DEFAULT_EXPRESSION)
        self.expr.trace_variable('w', self.var_debounce(self.expression_input))

        start_v = DoubleVar(self, value=self.st)
        end = DoubleVar(self, value=self.en)
        epsilon = DoubleVar(self, value=self.eps)
        divs = IntVar(self, value=self.div)
        lin_space_var = IntVar(self, value=self.lin_space_size)
        variables = (
            (start_v, 'st'),
            (end, 'en'),
            (epsilon, 'eps'),
            (divs, 'div')
        )

        def outer(var, var_name):
            def inner(*_args):
                try:
                    self.params_input(var.get(), var_name)
                except Exception:
                    pass
            return inner

        for (v, name) in variables:
            v.trace('w', self.debounce(outer(v, name), 250))
        lin_space_var.trace('w', self.debounce(lambda *_args: self.modify_lin_space_size(lin_space_var.get()), 250))

        self.frame.columnconfigure(1, weight=2)
        Label(self.frame, text='Выражение:').grid(column=0, row=0, columnspan=2, sticky='EW')
        Entry(self.frame, textvariable=self.expr).grid(column=0, row=1, columnspan=2, sticky='EW')

        self.frame.rowconfigure(2, minsize=25)
        Label(self.frame, text='Начало').grid(column=0, row=3, sticky='W')
        Entry(self.frame, textvariable=start_v).grid(column=1, row=3, sticky='EW')

        Label(self.frame, text='Конец').grid(column=0, row=4, sticky='W')
        Entry(self.frame, textvariable=end).grid(column=1, row=4, sticky='EW')

        Label(self.frame, text='Точность').grid(column=0, row=5, sticky='W')
        Entry(self.frame, textvariable=epsilon).grid(column=1, row=5, sticky='EW')

        Label(self.frame, text='Разделение').grid(column=0, row=6, sticky='W')
        Entry(self.frame, textvariable=divs).grid(column=1, row=6, sticky='EW')

        w = Scale(self.frame, from_=1, to=400, orient=HORIZONTAL, variable=lin_space_var)
        w.grid(column=0, row=7, columnspan=2, sticky='EW')

        self.tree = Treeview(self.frame)
        self.tree['columns'] = (1, 2, 3)
        self.tree.column('#0', width=25)
        self.tree.column(1, width=80, anchor='center')
        self.tree.column(2, width=80, anchor='center')
        self.tree.column(3, width=80, anchor='center')
        self.tree.heading('#0', text='№')
        self.tree.heading(1, text='x')
        self.tree.heading(2, text='y')
        self.tree.heading(3, text='iter')

        self.tree.grid(column=0, row=7, columnspan=2, sticky='EWSN')

    def modify_lin_space_size(self, size):
        self.lin_space_size = size
        self.redraw_main_plot(True)

    def redraw_main_plot(self, draw=False):
        if self.st != self.lin_x.min() or self.en != self.lin_x.max() or self.lin_space_size != len(self.lin_x):
            self.lin_x = np.linspace(self.st, self.en, self.lin_space_size)

        if self.main_plot:
            self.main_plot.remove()
        v = self.f(self.lin_x)
        self.main_plot = self.ax.plot(self.lin_x, v, label='f(x)')[0]
        mx_y = max(v)
        mn_y = min(v)
        m = (mx_y - mn_y) / 50
        self.ax.set_ylim(mn_y - m, mx_y + m)
        self.ax.set_xlim(self.st, self.en)
        if draw:
            self.fagg.draw()

    # Первичное отображение, подготавливает все данные для него.
    def prepare(self):
        step = (self.en - self.st) / self.div

        self.redraw_main_plot()

        for plt in self.plots:
            plt.remove()
        self.plots.clear()
        for line in self.h_lines:
            line.remove()
        self.h_lines.clear()

        for i in range(self.div+1):
            x = (self.st + step * i)
            self.h_lines.append(
                self.ax.axvline(x, color='black')
            )

        self.plots = [
            self.ax.plot(self.lin_x, self.solver.hord.k * self.lin_x + self.solver.hord.b, label='lin')[0],
            self.ax.scatter([self.solver.p1.x], [self.solver.p1.y], marker='o', color='red'),
            self.ax.scatter([self.solver.p_fixed.x], [self.solver.p_fixed.y], marker='o', color='blue')
        ]
        # self.ax.autoscale(axis='x')
        self.fagg.draw()

    def var_debounce(self, func: Callable[[str], None], t: int = 500) -> Callable:
        def inner(*args):
            func(self.tk.globalgetvar(args[0]))
        return self.debounce(inner, t)

    def debounce(self, func: Callable[..., None], t: int = 500) -> Callable:
        return Debouncer(self, func, t)

    def expression_input(self, value):
        try:
            self.cached_function = eval('lambda x: ' + value)
            self.reset()
        except Exception:
            pass
        print(value)

    def params_input(self, value, var_name):
        self.__setattr__(var_name, value)
        self.reset()
        print(value, var_name)

    def reset(self):
        self.started = False
        self.done = False
        self.tree.delete(*self.solutions)
        self.solutions.clear()
        self.solver = HordEquationSolver(self.st, self.en, self.div, self.eps, self.f)
        self.b_start.configure(text='start')
        self.b_start.bind('<Button>', self.start)
        self.prepare()

    def start(self, event):
        self.started = True
        self.paused = False
        event.widget.configure(text='stop')
        event.widget.bind('<Button>', self.stop)
        self.step_solve()

    def stop(self, event):
        self.paused = True
        event.widget.configure(text='start')
        event.widget.bind('<Button>', self.start)

    # Перерисовка хорды и точек пересечения.
    def redraw_solution(self):
        for pt in self.plots:
            pt.remove()
        self.plots = [
            self.ax.plot(self.lin_x, self.solver.hord.k * self.lin_x + self.solver.hord.b, label='lin', color='orange')[0],
            self.ax.scatter([self.solver.p1.x], [self.solver.p1.y], marker='o', color='red'),
            self.ax.scatter([self.solver.p_fixed.x], [self.solver.p_fixed.y], marker='o', color='blue')
        ]
        self.fagg.draw()
        self.ax.relim()

    def step_solve(self):
        if self.started and not self.solver.done:
            status = self.solver.next_step()
            if not status:
                self.redraw_solution()
                if self.started and not self.paused and not self.STEP_MODE:
                    self.after(100, self.step_solve)
            else:
                sol = (self.solver.p1.x, self.solver.p1.y, self.solver.iter_count)
                id = self.tree.insert('', 'end', 'iid' + str(len(self.solutions)), text=str(len(self.solutions)+1), values=sol)
                self.solutions.append(id)
                if self.solver.next_segment():
                    print('DONE!!!!')
                    self.b_start.configure(text='DONE!!!!')
                else:
                    if not self.STEP_MODE:
                        self.after(200, self.step_solve)


app = App(g_st, g_en, g_div, g_eps)
app.mainloop()
