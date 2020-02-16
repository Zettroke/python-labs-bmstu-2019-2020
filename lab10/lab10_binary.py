from typing import BinaryIO, List
import pickle
import hashlib


##
# Медяновский Олег ИУ7-14Б
# Простая бинарная база данных.
# Должна поддерживать операции:
# 1) Открытия БД
# 2) Создания БД
# 3) Вывести таблицу
# 4) Поиск по 1 полю
# 5) Поиск по 2 полям
# 6) Добавить запись


def from_bytes(bts: bytes) -> int:
    return int.from_bytes(bts, 'big')


def to_bytes(num: int, ln: int) -> bytes:
    return num.to_bytes(ln, 'big')


class FileDict:
    """
        Словарь хранящийся на диске, позволяет осуществлять поиск не загружая всех данных с диска.
        Возможность увеличения кол-ва корзин без создания нового словаря отсутствует.

        Структура:
        01E6 - signature
        bucket_count - 8 bytes число корзин
        size - 8 bytes длинна списка имен столбцов
        pickled names tuple - size bytes список имен столбцов записанный с помощью pickle
        bucket_table - bucket_count * 8 bytes массив относительных ссылок на данные корзин
        size_1 - 8 bytes
        bucket_1 - size_1 bytes
        size_2 - 8 bytes
        bucket_2 - size_2 bytes
        size_3 - 8 bytes
        bucket_3 - size_3 bytes
        ......
        size_n - 8 bytes длина n корзины
        bucket_n - size_n bytes данные n корзины, закодированные pickle

    """
    DEFAULT_BUCKET_COUNT = 256
    SIGNATURE = b'\x01\xE6'
    file: BinaryIO
    file_len: int
    bucket_count: int
    names: [str]

    def __init__(self, file: BinaryIO, default_bucket_count=DEFAULT_BUCKET_COUNT, names=('Название', 'Количество', 'Цена')):
        """
        Коснтруктор словаря, если передан пустой файл, то стандартно заполняет его DEFAULT_BUCKET_COUNT массивов
        :param file:
        :param default_bucket_count:
        :param names:
        """
        self.file = file
        self.file_len = self.file.seek(0, 2)
        self.header_pos = 8
        self.data_section_begin = 0

        if self.file_len == 0:
            self.file.write(self.SIGNATURE)
            self.file.write(to_bytes(default_bucket_count, 8))  # Инициализирую кол-во корзин.
            self.names = names
            names_data = pickle.dumps(self.names)
            l = pickle.dumps([])
            table = b''.join([
                to_bytes((i * (8 + len(l))), 8)
                for i in range(default_bucket_count)
            ])
            dd = to_bytes(len(l), 8) + l
            data = dd * default_bucket_count
            self.file.write(to_bytes(len(names_data), 8))
            self.file.write(names_data)
            self.file.write(table)
            self.file.write(data)
            self.file.flush()
            self.header_pos = 2 + 8 + 8 + len(names_data)
            self.bucket_count = default_bucket_count
            self.data_section_begin = self.header_pos + 8*self.bucket_count
        else:
            self.file.seek(0)
            if self.file.read(2) != self.SIGNATURE:
                raise Exception('wrong signature')
            self.bucket_count = from_bytes(self.file.read(8))
            names_len = from_bytes(self.file.read(8))
            self.names = pickle.loads(self.file.read(names_len))
            self.header_pos = 2 + 8 + 8 + names_len
            self.data_section_begin = self.header_pos + self.bucket_count * 8

    def __getitem__(self, item: str) -> List:
        """
        Получение списка элементов по ключу
        :param item:
        :return:
        """
        ind = from_bytes(hashlib.md5(item.encode()).digest()) % self.bucket_count

        self.file.seek(self.header_pos + ind*8)
        bucket_offset = from_bytes(self.file.read(8))
        self.file.seek(self.data_section_begin + bucket_offset)
        data_len = from_bytes(self.file.read(8))
        data = self.file.read(data_len)
        item = pickle.loads(data)
        return item

    def __setitem__(self, key: str, value: List):
        """
        Запись элемента по ключу, сразу записывает в файл
        :param key:
        :param value:
        :return:
        """
        ind = from_bytes(hashlib.md5(key.encode()).digest()) % self.bucket_count

        self.file.seek(self.header_pos + ind * 8)
        bucket_offset = from_bytes(self.file.read(8))
        self.file.seek(self.data_section_begin + bucket_offset)

        write_to = self.data_section_begin + bucket_offset + 8  # Позиция для записи данных

        data_len_prev = from_bytes(self.file.read(8))  # Длинна перезаписываемых данных
        data = pickle.dumps(value)  # Новые данные

        delta = len(data) - data_len_prev  # Вычисляю на сколько изменилась длинна данных
        buff_len = min(1024, len(data))

        if delta != 0:
            # Если длина элемента изменилась, то надо обновить таблицу ссылок
            self.file.seek(self.data_section_begin + bucket_offset)
            self.file.write(to_bytes(len(data), 8))  # Пишем новую длинну данных

            # Смещение остатка файла на delta байт
            self.file.seek(write_to + data_len_prev)
            buff = self.file.read(buff_len)
            buff2 = self.file.read(buff_len)
            self.file.seek(write_to)
            self.file.write(data)

            while len(buff) != 0:
                self.file.write(buff)
                buff = buff2
                self.file.seek(buff_len - delta, 1)
                buff2 = self.file.read(buff_len)
                self.file.seek(-(len(buff2) + buff_len - delta), 1)

            # Читаю и инкрементирую ссылки в заголовке.
            self.file.seek(self.header_pos)
            t = self.file.read(self.bucket_count*8)
            header = [from_bytes(b) for b in (
                t[i*8:(i+1)*8] for i in range(self.bucket_count)
            )]
            for i in range(ind+1, self.bucket_count):
                header[i] += delta
            header_bytes = b''.join([to_bytes(i, 8) for i in header])

            if delta < 0:
                # Если элемент уменьшился, то уменьшаю объем файла
                last_offset = header[-1]
                self.file.seek(self.data_section_begin + last_offset)
                sz = from_bytes(self.file.read(8))

                self.file.seek(sz, 1)
                self.file.truncate()

            self.file.seek(self.header_pos)
            self.file.write(header_bytes)
        else:
            self.file.seek(write_to)
            self.file.write(data)

        self.file.flush()

    def values(self) -> iter:
        """
        Итератор по всем значениям словаря
        :return:
        """
        def it(file, data_section_begin):
            file.seek(data_section_begin)
            while True:
                sz = file.read(8)
                if not sz:
                    break

                sz = from_bytes(sz)
                if sz == 0:
                    continue
                res = pickle.loads(file.read(sz))
                yield res

        return it(self.file, self.data_section_begin)


def open_db():
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
                    file = open(fname, 'r')
                    # Если файл существует то открываем его в двойном режиме
                    file = open(fname, 'rb+')
                    if file.read(2) == FileDict.SIGNATURE:
                        # Файл уже в бинарном формате
                        file.seek(0)
                        data = FileDict(file)
                        return data
                    else:
                        # Перевожу текстовый файл в бинарный формат.
                        file.close()
                        file = open(fname, 'r', encoding='utf-8')
                        open(fname + '.dat', 'wb')
                        names = file.readline().split()
                        data = FileDict(open(fname + '.dat', 'rb+'), names=names)
                        for l in file:
                            row = dict(zip(names, l.split()))
                            k = row[names[0]]
                            arr = data[k]
                            arr.append(row)
                            data[k] = arr
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
                        open(fname, 'w')  # Открываем файл в режими записи что бы он был создан
                        return FileDict(open(fname, 'wb+'))
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
    fields = d.names  # Читаю заголовок таблицы

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

    print('Добавалено!')


fields = []
col_lens = []
col_fmt = []
data_pos = 0

# file = open_db()
d = open_db()
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
            d.file.close()

            d = open_db()
            init_metadata()
            continue
        if act == 5:
            d.file.close()
            break
        actions[act]()
        print('-'*(sum(col_lens) + len(fields)))
    except Exception as e:
        if not act_raw.isnumeric() or act < 0 or act >= len(actions):
            print('Некорректный номер действия!')
        else:
            print('При выполнение операции произошла ошибка!')
