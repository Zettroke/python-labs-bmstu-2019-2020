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

##
# Медяновский Олег ИУ7-14Б
# Ввести матрицу A(6, 6), получить матрицу B(6, 5) путем вычеркивания главной диагонали.
# Найти столбец с максимальным кол-вом положительных элементов,
#  напечатать итоговую матрицу, номер столбца и кол-во элементов.
#


# Ввод размера матрицы
m = 6
mat = []
s = input('Введите размер квадратной матрицы: ')
if s.isnumeric() or (s[0] == '+' and s.isnumeric()):
    m = int(s)
else:
    print('Введите корректный размер квадратной матрицы')


print('Введите матрицу {}х{}:'.format(m, m))
# Ввод матрицы
while len(mat) < m:
    l = input('{}: '.format(len(mat) + 1)).split()
    is_num = True
    for i in l:
        is_num = is_num and test_num(i)
    if len(l) != m or not is_num:
        if not is_num:
            print('Введите корректные числа!')
        else:
            print('Введите строку из {} элементов!'.format(m))
    else:
        mat.append(list(map(float, l)))

# Удаление главной диагонали
for i in range(m):
    del mat[i][i]

# Подсчет полоительных элементов0
max_col = (-1, -1)  # (col, number)
for col in range(m-1):
    cnt = 0
    for row in mat:
        if row[col] > 0:
            cnt += 1
    if cnt > max_col[1]:
        max_col = (col+1, cnt)
if max_col == (-1, -1):
    print('Положительные элементы отсутствуют.')
else:
    for row in mat:
        for col in row:
            print(col, end=' ')
        print()
    print('{} столбец содержит максимальное кол-во положительных элементов: {}.'
          .format(*max_col))


'''
-1 -2 3 4 5 6
-7 8 -9 0 1 -2
3 4 -5 6 -7 -8
-9 -0 1 -2 -3 4
5 -6 -7 -8 9 0
-1 2 3 -4 5 -6
'''