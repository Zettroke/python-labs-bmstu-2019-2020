eps = float(input())
n = 1
v = 1
res = 0
sign = 1
while abs(v)*4 > eps:
    v = sign * 1/(2*n-1)
    res += v
    n += 1
    sign = -sign

print()
print('Сумма ряда сошлась на шаге {} с суммой: {:.9}'.format(n, 4*res))