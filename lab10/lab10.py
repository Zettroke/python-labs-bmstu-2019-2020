from typing import List

##
# Медяновский Олег ИУ7-14Б
# Простая текстовая база данных.
# Должна поддерживать операции:
# 1) Открытия БД
# 2) Создания БД
# 3) Вывести таблицу
# 4) Поиск по 1 полю
# 5) Поиск по 2 полям
# 6) Добавить запись


# Открытие или создание файла БД
def open_db():
    file = None
    while not file:
        try:
            print('1. Открыть базу данных')
            print('2. Создать базу данных')
            action = int(input())
            fname = input('Введите имя файла: ')
            if action == 1:
                try:
                    file = open(fname, 'r')
                    # Если файл существует то открываем его в двойном режиме
                    file = open(fname, 'r+', encoding='utf-8')
                except Exception:
                    print('Файла не существует!')
            elif action == 2:
                try:
                    # Пытаемся открыть файл, если вышло, значит он существует
                    open(fname, 'r')
                    print('Файл уже существует! Введите другое имя файла!')
                    continue
                except Exception:
                    try:
                        open(fname, 'w')  # Открываем файл в режими записи что бы он был создан
                        file = open(fname, 'r+', encoding='utf-8')
                        file.write('Название Количество Цена\n')
                        file.seek(0)
                    except Exception:
                        print('Ошибка создания файла!')
            else:
                print('Неизвестное действие!')
        except Exception:
            print('Некорректный формат номера действия!')
    return file


# Инициализвация метаданных, заголовков, ширины строк.
def init_metadata():
    global fields, data_pos, col_lens, col_fmt
    fields = file.readline().split()  # Читаю заголовок таблицы
    data_pos = file.seek(0, 1)  # Сохраняем позицию с которой начинаются данные

    # Вычисление выравнивания столбцов
    col_lens = [len(f) + 6 for f in fields]
    for l in file:
        for i, c in enumerate(l.split()):
            col_lens[i] = max(col_lens[i], len(c) + 6)
    col_fmt = ['{:^' + str(l) + '}' for l in col_lens]


# Переместить каретку к началу данных
def seek_to_data():
    file.seek(data_pos)


def print_header():
    for i, f in enumerate(fields):
        print(col_fmt[i].format(f), end='|')
    print()
    print('-'*(sum(col_lens) + len(col_lens)))


# Вывод строки с учетом форматирования
def print_row(row: List[str]):
    for i, f in enumerate(row):
        print(col_fmt[i].format(f), end='|')
    print()


# Печать всей таблицы
def print_table():
    seek_to_data()
    print_header()
    for l in file:
        print_row(l.split())


# Поиск по 1 полю
def find_by():
    seek_to_data()
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
    for l in file:
        if l.split()[f_pick] == search:
            res.append(l.split())
    if len(res) == 0:
        print('Ничего не найдено!')
    else:
        print_header()
        print('Найдено {} записей:'.format(len(res)))
        for r in res:
            print_row(r)


# Поиск по 2 полям
def find_by_two():
    seek_to_data()
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
    res = []
    for l in file:
        if l.split()[f_pick[0]] == search1 and l.split()[f_pick[1]] == search2:
            res.append(l.split())
    if len(res) == 0:
        print('Ничего не найдено!')
    else:
        print('Найдено {} записей:'.format(len(res)))
        print_header()
        for r in res:
            print_row(r)


# Добавление записи
def append():
    global col_fmt
    # Перемещаюсь в конец файла для записи
    file.seek(0, 2)
    print('Введите данные для добавления:')
    row = []
    for i, f in enumerate(fields):
        row.append(input('{}) {}: '.format(i, f)))
    file.write(' '.join(row) + '\n')
    file.flush()

    # Обновляю выравнивание столбцов
    for i, c in enumerate(row):
        col_lens[i] = max(col_lens[i], len(c) + 6)
    col_fmt = ['{:^' + str(l) + '}' for l in col_lens]
    print('Добавалено!')


fields = []
col_lens = []
col_fmt = []
data_pos = 0

file = open_db()
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
        act_raw = input()
        act = int(act_raw)-1
        if act == 4:
            file.close()

            file = open_db()
            init_metadata()
            continue
        if act == 5:
            file.close()
            break
        actions[act]()
        print('-'*(sum(col_lens) + len(fields)))
    except Exception as e:
        if not act_raw.isnumeric() or act < 0 or act >= len(actions):
            print('Некорректный номер действия!')
        else:
            print('При выполнение операции произошла ошибка!')
