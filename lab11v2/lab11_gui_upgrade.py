##
# Медяновский Олег ИУ7-14Б
# Программа вычисляет корни функции на заданном интервале
# с определённым шагом разбиений методом хорд и выводит таблицу корней.
import traceback


from tkinter.ttk import Treeview
from typing import Callable, List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Tk, Button, Frame, Entry, Label, StringVar, DoubleVar, IntVar, Scale, HORIZONTAL, Checkbutton

from matplotlib.lines import Line2D

from lab11v2.lab11_solver import HordEquationSolver, Solution
import math

DELAY_MS = 50
X_CHANGE_REDRAW_COEF = 500  # 0.000000001  # 500

g_st, g_en = -10, 10
g_eps = 0.00000001
g_div = 9
ITER_LIMIT = 10_000  # Ограничение по числу итераций.
DELTA_THRESHOLD = (g_en - g_st) / X_CHANGE_REDRAW_COEF  # Изменение x при котором вызывается перерисовка.
# DEFAULT_EXPRESSION = '8*x**4-5*(x-0.1)+1'
DEFAULT_EXPRESSION = 'np.sin(x)'
LOG_BASE = 5
MAX_LINE_SPACE_SIZE = 4000


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
            self.func(*args, **kwargs)
        self.last_job_id = self.tk.after(self.t, self.func, *args)


class App(Tk):
    STEP_MODE: IntVar  # Пошаговое проигрывание анимации.
    SHOW_INFLECTION_POINTS: IntVar

    started = False  # Мы начали искать корни, в это время нельзя менять менять уравнение.
    paused = False  # Пауза для анимации.
    done: bool = False
    st: float
    en: float
    div: int
    eps: float

    lin_x: any  # Множество точек для построения графика.
    lin_space_size: int = 400  # Кол-во точек для построения графика

    solver: HordEquationSolver

    expr: StringVar  # Введенное пользователем выражение

    # График
    ax: plt.Axes
    plots: List[Line2D] = []
    h_lines: List[Line2D] = []  # Горизонтальные линии
    main_plot: any = None
    deriv_plot: any = None
    inflection_points: any = None

    # Список решений
    solutions: List[Solution] = []
    solution_ids: List[str] = []

    tree: Treeview  # Таблица результатов
    b_start: Button  # Кнопка начала/остановки
    lin_space_label: Label  # Надпись о точности графика

    cached_function: any  # Декодированная функция, что бы каждый раз не вызывать eval
    after_job_id: any = None  # id отложенного вызова функции для её отмены

    def f(self, x):
        return self.cached_function(x)

    def __init__(self, st: float, en: float, div: int, eps: float):
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
        self.frame = Frame(self)
        self.frame.grid(row=0, column=1, sticky='WNSE', rowspan=2)

        self.init_sidebar()

        self.solver = HordEquationSolver(st, en, div, eps, self.f)

        self.prepare()

        self.fagg.draw()
        button_frame = Frame(self)
        button_frame.grid(row=1, column=0, sticky='WE')
        self.b_start = Button(button_frame, text='start')
        self.b_start.pack(side='left', anchor='center')
        self.b_start.bind('<Button>', self.start)
        Button(button_frame, text='reset', command=self.reset).pack(side='left', anchor='center')

    def init_sidebar(self):
        self.cached_function = eval('lambda x: ' + DEFAULT_EXPRESSION)
        self.expr = StringVar(self)
        self.expr.set(DEFAULT_EXPRESSION)
        self.expr.trace_variable('w', self.var_debounce(self.expression_input))

        # Динамические переменные для входных полей
        start_v = DoubleVar(self, value=self.st)
        end = DoubleVar(self, value=self.en)
        epsilon = DoubleVar(self, value=self.eps)
        divs = IntVar(self, value=self.div)
        lin_space_var = DoubleVar(self, value=math.log(self.lin_space_size, LOG_BASE))
        variables = (
            (start_v, 'st'),
            (end, 'en'),
            (epsilon, 'eps'),
            (divs, 'div')
        )

        # Функция обертка для сигнализирования о смене переменной.
        def outer(var, var_name):
            def inner(*_args):
                try:
                    self.params_input(var.get(), var_name)
                except Exception:
                    pass
            return inner

        for (v, name) in variables:
            v.trace('w', self.debounce(outer(v, name), 250))

        lin_debouncer = self.debounce(self.modify_lin_space_size, 150)
        lin_space_var.trace('w', lambda *_args: self.modify_lin_space_size_callback(lin_space_var.get(), lin_debouncer))

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

        self.frame.rowconfigure(7, minsize=25)
        self.lin_space_label = Label(self.frame, text=f'Количество точек графика: {self.lin_space_size}')
        self.lin_space_label.grid(column=0, row=8, columnspan=2, sticky='W')
        w = Scale(self.frame, from_=math.log(5, LOG_BASE), to=math.log(MAX_LINE_SPACE_SIZE, LOG_BASE), resolution=0.1/LOG_BASE, orient=HORIZONTAL, variable=lin_space_var)
        w.grid(column=0, row=9, columnspan=2, sticky='EW')

        self.tree = Treeview(self.frame)
        self.tree['columns'] = (1, 2, 3, 4, 5)
        self.tree.column('#0', width=35)
        self.tree.column(1, width=130, anchor='center')
        self.tree.column(2, width=80, anchor='center')
        self.tree.column(3, width=80, anchor='center')
        self.tree.column(4, width=80, anchor='center')
        self.tree.column(5, width=80, anchor='center')
        self.tree.heading('#0', text='№')
        self.tree.heading(1, text='Интервал')
        self.tree.heading(2, text='Корень')
        self.tree.heading(3, text='Значение')
        self.tree.heading(4, text='Итераций')
        self.tree.heading(5, text='Ошибка')

        self.tree.grid(column=0, row=10, columnspan=2, sticky='EWSN')

        self.STEP_MODE = IntVar(self, value=0)
        self.SHOW_INFLECTION_POINTS = IntVar(self, value=1)
        self.SHOW_INFLECTION_POINTS.trace('w', lambda *_args: self.redraw_main_plot(True))
        Checkbutton(self.frame, text='Пошаговый режим', variable=self.STEP_MODE).grid(column=0, row=11, sticky='WS')
        Checkbutton(self.frame, text='Показывать точка перегиба', variable=self.SHOW_INFLECTION_POINTS)\
            .grid(column=0, row=12, sticky='WS')

    def modify_lin_space_size_callback(self, value, callback):
        self.lin_space_label.configure(text=f'Количество точек графика: {round(LOG_BASE**value)}')
        callback(value)

    def modify_lin_space_size(self, size):
        self.lin_space_size = round(LOG_BASE**size)
        self.redraw_main_plot(True)

    def redraw_main_plot(self, draw=False):
        if self.st != self.lin_x.min() or self.en != self.lin_x.max() or self.lin_space_size != len(self.lin_x):
            self.lin_x = np.linspace(self.st, self.en, self.lin_space_size)

        if self.main_plot:
            self.main_plot.remove()
        if self.deriv_plot:
            self.deriv_plot.remove()
            self.deriv_plot = None
        if self.inflection_points:
            self.inflection_points.remove()
            self.inflection_points = None
        v = self.f(self.lin_x)
        if self.SHOW_INFLECTION_POINTS.get():
            v2 = np.diff(v)
            v2 = np.insert(v2, 0, v2[0] - (v2[1] - v2[0]))
            v2 /= ((self.en - self.st) / self.lin_space_size)

            v2 = np.diff(v2)
            v2 = np.append(v2, v2[-1])
            v2 /= ((self.en - self.st) / self.lin_space_size)
            inflection_points_x = []
            inflection_points_y = []
            for i in range(1, len(v2)):
                if v2[i-1] * v2[i] <= 0:
                    if v[i-1] == 0:
                        continue
                    n = i - 1 if v2[i-1] < v2[i] else i
                    x = self.st + (self.en - self.st) / self.lin_space_size * n
                    y = self.f(x)

                    inflection_points_x.append(x)
                    inflection_points_y.append(y)

            self.inflection_points = self.ax.scatter(inflection_points_x, inflection_points_y, 80, marker='x', color='violet')

            self.deriv_plot = self.ax.plot(self.lin_x, v2, label="f''(x)", color='tab:green')[0]

        self.main_plot = self.ax.plot(self.lin_x, v, label='f(x)', color='tab:blue')[0]
        mx_y = max(v)
        mn_y = min(v)
        m = (mx_y - mn_y) / 50
        dx = abs(self.en - self.st)*0.05
        self.ax.set_ylim(mn_y - m, mx_y + m)
        self.ax.set_xlim(self.st-dx, self.en+dx)
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
            self.ax.plot(self.lin_x, self.solver.hord.k * self.lin_x + self.solver.hord.b, label='lin', color='tab:orange')[0],
            self.ax.scatter([self.solver.p1.x], [self.solver.p1.y], marker='o', color='red'),
            self.ax.scatter([self.solver.p_fixed.x], [self.solver.p_fixed.y], marker='o', color='blue')
        ]
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
        except Exception as e:
            traceback.print_exc()
            print(e)
            pass

    def params_input(self, value, var_name):
        self.__setattr__(var_name, value)
        self.reset()

    def reset(self):
        if self.after_job_id:
            self.after_cancel(self.after_job_id)
        self.started = False
        self.done = False
        self.tree.delete(*self.solution_ids)
        self.solutions.clear()
        self.solution_ids.clear()
        self.solver = HordEquationSolver(self.st, self.en, self.div, self.eps, self.f)
        self.b_start.configure(text='start')
        self.b_start.bind('<Button>', self.start)
        self.prepare()

    def start(self, event):
        if self.STEP_MODE.get():
            self.step_solve()
        else:
            if not self.started or self.paused:
                self.started = True
                self.paused = False
                self.step_solve()
                event.widget.configure(text='stop')
                event.widget.bind('<Button>', self.stop)

    def stop(self, event):
        self.paused = True
        if self.after_job_id:
            self.after_cancel(self.after_job_id)
        event.widget.configure(text='start')
        event.widget.bind('<Button>', self.start)

    # Перерисовка хорды и точек пересечения.
    def redraw_solution(self):
        for pt in self.plots:
            pt.remove()
        self.plots = [
            self.ax.plot(self.lin_x, self.solver.hord.k * self.lin_x + self.solver.hord.b, label='lin', color='tab:orange')[0],
            self.ax.scatter([self.solver.p1.x], [self.solver.p1.y], marker='o', color='red'),
            self.ax.scatter([self.solver.p_fixed.x], [self.solver.p_fixed.y], marker='o', color='blue')
        ]
        self.fagg.draw()
        self.ax.relim()

    def step_solve(self):
        if self.started and not self.solver.done or self.STEP_MODE.get():
            status = self.solver.next_step()
            self.redraw_solution()
            if not status:
                if self.started and not self.paused and not self.STEP_MODE.get():
                    self.after_job_id = self.after(100, self.step_solve)
            else:
                self.add_solution(self.solver.get_solution())
                if self.solver.next_segment():
                    print('DONE!!!!')
                    self.b_start.configure(text='DONE!!!!')
                    self.b_start.unbind('<Button>')
                else:
                    self.redraw_solution()
                    if not self.STEP_MODE.get():
                        self.after_job_id = self.after(200, self.step_solve)

    def add_solution(self, sol):
        if sol.err == 0:
            interval = f'({sol.interval[0]:.5} : {sol.interval[1]:.5})'
            iid = self.tree.insert(
                '',
                'end',
                text=str(len(self.solutions)+1),
                values=(interval, f'{sol.x:.7}', f'{sol.y:.5}', sol.iter, sol.err)
            )
        else:
            iid = self.tree.insert('', 'end', text=str(len(self.solutions)+1), values=('', '', '', '', sol.err))
        self.solutions.append(sol)
        self.solution_ids.append(iid)


app = App(g_st, g_en, g_div, g_eps)
app.mainloop()
