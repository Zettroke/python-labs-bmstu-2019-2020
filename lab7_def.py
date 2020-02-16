# Символьная матрица, требуется удалит все столбцы содержащи хотя бы одну цифру.
mat = []
s = list(input('1: '))
m = len(s)

while True:
    if not s:
        break

    if len(s) == m:
        mat.append(s)
    else:
        print('Введите строку длиннов {}'.format(m))

    s = list(input('{}: '.format(len(mat)+1)))

if len(mat) == 0:
    print('Введена пустая матрица!')
else:
    col = 0
    while col < m:
        has_num = False
        coll = []
        for row in mat:
            coll.append(row[col])
            if row[col].isdigit():
                has_num = True
                break

        if has_num:
            for row in mat:
                del row[col]
            m -= 1
            col -= 1
        col += 1
    if len(mat[0]) == 0:
        print('Получилась пустая матрица!')
    else:
        for row in mat:
            for col in row:
                print(col, end=' ')
            print()

'''
1bcdefg
a1cdefg
ab1defg
abcd1fg
abcde1g
abcdef1
'''