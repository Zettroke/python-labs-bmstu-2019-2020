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
# Ввести матрицу X(10, 8), переписать все отрицательные элементы матрицы
# в массив D, без пропусков и упорядочить по убыванию.
# Напечатать матрицу X и массив D.
#


# Ввод размера матрицы
m, n = 10, 8
mat = []
l = input('Введите размер матрицы: ').split()
if len(l) == 2 and test_num(l[0]) and test_num(l[1]):
    m, n = map(int, l)
else:
    print('Введите 2 натуральных числа!')

print('Введите матрицу {}х{}:'.format(m, n))

# Ввод матрицы
while len(mat) < m:
    l = input('{}: '.format(len(mat) + 1)).split()
    is_num = True
    for i in l:
        is_num = is_num and test_num(i)
    if len(l) != n or not is_num:
        if not is_num:
            print('Введите корректные числа!')
        else:
            print('Введите строку из {} элементов!'.format(n))
    else:
        mat.append(list(map(float, l)))

D = []
# Переписывание отрицательных элементов
for row in range(len(mat)):
    for col in range(len(mat[row])):
        if mat[row][col] < 0:
            D.append(mat[row][col])
# Упорядочивание элементов
D.sort(key=lambda x: -x)

for row in mat:
    for col in row:
        print(col, end=' ')
    print()
print('Список отрицательных элементов матрицы: {}'.format(D))


'''
-1 -2 3 4 5 6 -1 8
-7 8 -9 0 1 -2 -2 -7
3 4 -5 6 -7 -8 -3 7
-9 -0 1 -2 -3 4 -7 7
5 -6 -7 -8 9 0 8 1
-1 2 3 -4 5 -6 9 0
5 -6 -7 -8 9 0 8 1
-1 2 3 -4 5 -6 9 0
3 4 -5 6 -7 -8 -3 7
-9 -0 1 -2 -3 4 -7 7
'''