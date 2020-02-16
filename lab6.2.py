##
# Медяновский Олег ИУ7-14Б
# Ввести массив чисел. (реализовать без срезов и с ними)
# 1. Вставить введенный элемент после последнего максимального элемента.
# 2. Вывести количество отрицательных элементов после минимального значения массива.
#


def test_num(n):
    if len(n) == 0:
        return False
    negative = int(n[0] == '-' or n[0] == '+')
    dot = n.find('.')
    e = n.find('e')
    frac_part = ''
    exp_part = ''

    if dot != -1:
        whole_part = n[negative:dot]
    elif e != -1:
        whole_part = n[negative:e]
    else:
        whole_part = n[negative:]

    if e != -1:
        if dot != -1:
            frac_part = n[dot + 1:e]
        exponent = n[e + 1:]
        if len(exponent) > 0:
            exp_part = exponent[int(exponent[0] == '-' or exponent[0] == '+'):]

        if e != -1 and not exp_part:
            exp_part = 'wrong'
    elif dot != -1:
        frac_part = n[dot + 1:]

    res = bool((whole_part or frac_part) and (not whole_part or whole_part.isnumeric()) and (not frac_part or frac_part.isnumeric()) and (
                not exp_part or exp_part.isnumeric()))

    return res


print('Введите элементы массива, каждый с новой строки(введите пустую строку для прекращения ввода):')
l = []
s = input('1 элемент: ').strip()
is_num = False
while s:  # Ввод массива
    is_num = test_num(s)
    if is_num:
        l.append(float(s))
    else:
        print('Некорректный формат, введите число заново!')
    s = input('{} элемент: '.format(len(l) + 1)).strip()

if len(l) == 0:
    print('Введен пустой массив!')
else:
    # Поиск минимального значения и подсчет отрицательных значений.
    neg_cnt = 0
    mn_value = l[0]
    for i in l:
        if i < 0:
            neg_cnt += 1

        if i <= mn_value:
            mn_value = i
            neg_cnt = 0
    print()
    print('Количество отрицательных чисел после минимального значения: {}'.format(neg_cnt))

