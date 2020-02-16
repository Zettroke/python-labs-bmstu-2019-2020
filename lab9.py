from typing import List, Optional
vowel = {'а', 'я', 'о', 'е', 'у', 'ю', 'ы', 'и', 'э', 'е'}  # Список гласных букв
current_text = [
    'Обучение в МГТУ им. Н.Э. Баумана ведется на 10+9 факультетах дневного обучения. Работает, аспирантура и',
    'докторантура, два профильных лицея.МГТУ им. Н.Э. Баумана осуществляет подготовку более 19 тысяч',
    'студентов практически по всему спектру современного машино- и приборостроения. Научную и учебную работу',
    '    ведут более 320 докторов и около 2000-199+7+-8+200 кандидатов наук. Основными структурными подразделениями',
    'Бауманского университета являются научно-учебные комплексы, имеющие в своем составе факультет и',
    'научно-исследовательский институт. Их — восемь (см. в колонке справа). ~амяв   - , о ж.',
    'АБАБАБ АБ А Б А. АААББА'
]
# current_text = [
#     '100-0 100+0 0+0 0-0 5-5 67+35'
#     ]


def is_char(c: str):
    return ord('а') <= ord(c.lower()) <= ord('я')


def text_iter(text):
    for l in text:
        for s in l:
            yield s


# Выравнивание по ширине
def align_width(text: List[str]):
    mx_len = 0
    temp = []
    for ind, l in enumerate(text):
        words = l.split()
        temp.append(words)
        mx_len = max(sum(len(s) for s in words) + len(words) - 1, mx_len)

    for ind, words in enumerate(temp):
        needed_spaces = mx_len - sum(len(s) for s in words)

        spaces_per_word = needed_spaces // (len(words) - 1)
        additional_spaces = needed_spaces % (len(words) - 1)
        res = [words[0]]
        for wind, w in enumerate(words[1:]):
            add_space = 0
            if wind < (additional_spaces // 2 + additional_spaces % 2) or len(words) - 1 - wind <= additional_spaces // 2:
                add_space = 1
            res.append(' '*(spaces_per_word + add_space))
            res.append(w)

        text[ind] = ''.join(res)


# Выравнивание по левому краю
def align_left(text: List[str]):
    for ind, l in enumerate(text):
        text[ind] = ' '.join(l.split())


# Выравнивание по правому краю
def align_right(text: List[str]):
    mx_len = 0
    for ind, l in enumerate(text):
        text[ind] = l.rstrip()
        mx_len = max(len(text[ind]), mx_len)

    for ind, l in enumerate(text):
        text[ind] = l.rjust(mx_len)


# Замена слова
def replace_word(text: List[str]):
    word_src = input('Введите слово которое заменять: ')
    word_dst = input('Введите слово на которое заменять: ')
    for ind, l in enumerate(text):
        w = l.find(word_src)
        while w != -1:
            if (w == 0 or not is_char(l[w-1])) and (w + len(word_src) >= len(l) or not is_char(l[w + len(word_src)])):
                l = l[:w] + word_dst + l[w + len(word_src):]
            w = l.find(word_src, w)

        text[ind] = l


# Удаление слова
def remove_word(text: List[str]):
    word_src = input('Введите слово для удаления: ')
    for ind, l in enumerate(text):
        w = l.find(word_src)
        while w != -1:
            if (w == 0 or not is_char(l[w - 1])) and (w + len(word_src) >= len(l) or not is_char(l[w + len(word_src)])):
                st = 0
                while w-st-1 >= 0 and l[w-st-1] == ' ':
                    st += 1
                l = l[:w - st] + l[w + len(word_src):]
            w = l.find(word_src, w+1)

        text[ind] = l


# Подсчет строкового выражение, возвращает None если оно некорректно, или состоит из 1 числа.
def calculate(expr: str) -> Optional[int]:
    if len(expr) == 1 or expr.isdigit() or expr[1:].isdigit():
        return None
    else:
        try:
            res = 0
            first = True
            op = '+'
            curr = []
            for i in expr[:]:
                if i.isdigit() or first:
                    curr.append(i)
                    first = False
                else:
                    n = int(''.join(curr))
                    if op == '+':
                        res += n
                    else:
                        res -= n
                    first = True
                    op = i
                    curr.clear()
            if len(curr) > 0:
                res += int(''.join(curr))
        except:
            return None
        return res


# Подсчет и вставка результатов арифметический выражений в тексте
def arithmetic_transform(text: List[str]):
    for text_ind, l in enumerate(text):
        res = []
        expressions = []
        expr = False
        expr_buf = []
        prev_expr_end = 0
        begin = -1
        for ind, i in enumerate(l):
            if i.isdigit() or i == '-' or i == '+':
                if not expr:
                    expr = True
                    begin = ind
                    expr_buf.append(i)
                else:
                    expr_buf.append(i)
            elif expr and i == ' ':
                expr = False
                data = ''.join(expr_buf)
                v = calculate(data)
                if v is not None:
                    res.append(l[prev_expr_end:begin])
                    res.append(str(v))
                    prev_expr_end = begin + len(data)
                expr_buf.clear()
            elif expr:
                expr = False
                expr_buf.clear()
        if expr:
            data = ''.join(expr_buf)
            v = calculate(data)
            if v is not None:
                res.append(' ' + str(v))
        else:
            res.append(l[prev_expr_end:])

        text[text_ind] = ''.join(res)


#
def alternating_sentence(text: List[str]):
    res = []
    sentence = []
    is_alternating = True
    chrs = 0
    is_vowel = None
    for i in text_iter(text):
        sentence.append(i)
        i = i.lower()
        if i == '.' or i == '!' or i == '?':
            if is_alternating and chrs >= 2:
                res.append(''.join(sentence).lstrip())
            is_alternating = True
            sentence.clear()
            chrs = 0
        elif ord('а') <= ord(i) <= ord('я'):
            if chrs == 0:
                is_vowel = i in vowel
                chrs += 1
                continue
            tmp = i in vowel
            is_alternating = is_alternating and is_vowel != tmp
            is_vowel = tmp
            chrs += 1

    return res


actions = [
    align_width,
    align_left,
    align_right,
    replace_word,
    remove_word,
    arithmetic_transform,
    alternating_sentence,
    lambda text: exit()
]
for l in current_text:
    print(l)

while True:

    print('Выберите действие:')
    print('1) Выравнить текст по ширине')
    print('2) Выравнить текст по левому краю')
    print('3) Выравнить текст по правому краю')
    print('4) Замена слова')
    print('5) Удаление слова')
    print('6) Раскрытие арифметических выражений')
    print('7) Поиск предложений с чередующимися гласными и согласными')
    print('8) Выход')

    try:
        n = int(input('Номер действия: '))
        action = actions[n-1]
    except (ValueError, IndexError):
        print('Некорректный номер действия!')
        continue

    res = action(current_text)

    print('\n'*10)
    if res:
        for i in res:
            print(i)
    print()
    for l in current_text:
        print(l)
