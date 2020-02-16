from typing import List, Tuple
import pickle


def from_bytes(bts: bytes) -> int:
    return int.from_bytes(bts, 'big')


def to_bytes(num: int, ln: int) -> bytes:
    return num.to_bytes(ln, 'big')


def open_db() -> Tuple[str, List[str], dict]:
    file = None
    data = None
    while not file:
        try:
            print('1. Открыть базу данных')
            print('2. Создать базу данных')
            action = int(input())
            fname = input('Введите имя файла: ')
            if action == 1:
                try:
                    file = open(fname, 'rb')
                    # Если файл существует то открываем его в двойном режиме
                    try:
                        d = pickle.load(file)
                        return fname, d[0], d[1]
                    except Exception:
                        file = open(fname, 'r', encoding='utf-8')
                        names = file.readline().split()
                        d = {}
                        for l in file:
                            ll = l.split()
                            temp = d.get(ll[0], [])
                            temp.append(dict(zip(names, ll)))
                            d[ll[0]] = temp
                        data = (fname + '.dat', names, d)
                        pickle.dump(data, open(fname + '.dat', 'wb'))
                        return data

                except Exception as e:
                    print(e)
                    print('Файла не существует!')
            elif action == 2:
                try:
                    # Пытаемся открыть файл, если вышло, значит он существует
                    open(fname, 'r')
                    print('Файл уже существует! Введите другое имя файла!')
                    continue
                except Exception:
                    try:
                        file = open(fname, 'wb')  # Открываем файл в режими записи что бы он был создан
                        d = (['Название', 'Количество', 'Цена'], {})
                        pickle.dump(d, file)
                        return fname, ['Название', 'Количество', 'Цена'], {}
                    except Exception:
                        print('Ошибка создания файла!')
            else:
                print('Неизвестное действие!')
        except Exception:
            print('Некорректный формат номера действия!')
    return data


# Инициализвация метаданных, заголовков, ширины строк.
def init_metadata():
    global fields, data_pos, col_lens, col_fmt

    # Вычисление выравнивания столбцов
    col_lens = [len(f) + 6 for f in fields]
    for l in d.values():
        for v in l:
            for i, k in enumerate(fields):
                col_lens[i] = max(col_lens[i], len(v[k]) + 6)
    col_fmt = ['{:^' + str(l) + '}' for l in col_lens]


def print_header():
    for i, f in enumerate(fields):
        print(col_fmt[i].format(f), end='|')
    print()
    print('-'*(sum(col_lens) + len(col_lens)))


# Вывод строки с учетом форматирования
def print_row(row: dict):
    for i, k in enumerate(fields):
        print(col_fmt[i].format(row[k]), end='|')
    print()


# Печать всей таблицы
def print_table():
    print_header()
    for l in d.values():
        for v in l:
            print_row(v)


# Поиск по 1 полю
def find_by():
    print('Выберите поле для поиска:')
    while True:
        try:
            for i, f in enumerate(fields):
                print('{}) {}'.format(i+1, f))
            f_pick = int(input()) - 1

            if f_pick >= len(fields) or f_pick < 0:
                print('Некорректный номер столбца')
            else:
                break
        except Exception:
            print('Некорректный номер столбца')
    search = input('Введите искомое значение: ')
    res = []
    if f_pick == 0:
        for v in d[search]:
            if v[fields[f_pick]] == search:
                res.append(v)
    else:
        for l in d.values():
            for v in l:
                if v[fields[f_pick]] == search:
                    res.append(v)
    if len(res) == 0:
        print('Ничего не найдено!')
    else:
        print('Найдено {} записей:'.format(len(res)))
        print_header()
        for r in res:
            print_row(r)


# Поиск по 2 полям
def find_by_two():
    print('Выберите 2 поля для поиска:')
    while True:
        try:
            for i, f in enumerate(fields):
                print('{}) {}'.format(i+1, f))
            f_pick = [int(v)-1 for v in input('Введите два номера из списка выше: ').split()]
            if f_pick[0] >= len(fields) or f_pick[0] < 0 or f_pick[1] >= len(fields) or f_pick[1] < 0:
                print('Некорректный номер столбца')
            elif f_pick[0] == f_pick[1]:
                print('Номера не должны совпадать')
            else:
                break
        except Exception:
            print('Некорректный номер столбца')

    search1 = input('Введите искомое значение 1: ')
    search2 = input('Введите искомое значение 2: ')

    indexed = False
    if f_pick[1] == 0:
        search2, search1 = search1, search2
        f_pick = reversed(f_pick)
        indexed = True
    elif f_pick[0] == 0:
        indexed = True

    res = []
    if indexed:
        for v in d[search1]:
            if v[fields[f_pick[0]]] == search1 and v[fields[f_pick[1]]] == search2:
                res.append(v)
    else:
        for l in d.values():
            for v in l:
                if v[fields[f_pick[0]]] == search1 and v[fields[f_pick[1]]] == search2:
                    res.append(v)
    if len(res) == 0:
        print('Ничего не найдено!')
    else:
        print_header()
        print('Найдено {} записей:'.format(len(res)))
        for r in res:
            print_row(r)


# Добавление записи
def append():
    global col_fmt
    print('Введите данные для добавления:')
    row = {}
    for i, f in enumerate(fields):
        row[f] = input('{}) {}: '.format(i, f))

    temp = d.get(row[fields[0]], [])
    temp += [row]
    d[row[fields[0]]] = temp

    # Обновляю выравнивание столбцов
    for l in d.values():
        for v in l:
            for i, k in enumerate(fields):
                col_lens[i] = max(col_lens[i], len(v[k]) + 6)
    col_fmt = ['{:^' + str(l) + '}' for l in col_lens]

    pickle.dump((fields, d), open(fname, 'wb'))

    print('Добавалено!')


col_lens = []
col_fmt = []
data_pos = 0

# file = open_db()
fname, fields, d = open_db()
init_metadata()

actions = [
    print_table,
    find_by,
    find_by_two,
    append,
]
while True:
    try:
        print('''
1) Вывести таблицу
2) Поиск по 1 полю
3) Поиск по 2 полям
4) Добавить запись
5) Сменить БД
6) Выход
        ''')
        act = int(input())-1
        if act == 4:
            fname, fields, d = open_db()
            init_metadata()
            continue
        if act == 5:
            break
        actions[act]()
        print('-'*(sum(col_lens) + len(fields)))
    except Exception as e:
        print(e)
        if act < 0 or act >= len(actions):
            print('Некорректный номер действия!')
        else:
            print('При выполнение операции произошла ошибка!')
