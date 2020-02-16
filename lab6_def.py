# Дан массив, удалить отрицательные элементы без всего

l = list(map(float, input().split()))

curr_pos = 0
taker_pos = 0

for curr_pos in range(len(l)):
    if taker_pos == len(l):
        break
    for i in range(taker_pos, len(l)):
        if l[i] > 0:
            l[curr_pos] = l[i]
            taker_pos = i + 1
            break
l = l[:curr_pos]
print(l)