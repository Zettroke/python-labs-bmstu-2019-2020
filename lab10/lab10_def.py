# Дан текстовый файл, требуется переписать в новый файл все строки исходного файла в обратном порядке.
buff = []
STEP = 128
fin = open('input', 'rb')
fout = open('output', 'wb')

pos = fin.seek(0, 2)
n = STEP
while pos != 0:
    fin.seek(pos)

    data = fin.read(n)
    if b'\n' in data:
        lines = data.split(b'\n')
        fout.write(lines[-1] + b''.join(reversed(buff)) + b'\n')
        buff.clear()
        if len(lines) > 2:
            for l in lines[-2:0:-1]:
                fout.write(l + b'\n')
        buff.append(lines[0])
    else:
        buff.append(data)

    n = min(pos, STEP)
    pos = max(0, pos-STEP)

fin.seek(0)
data = fin.read(n)
if data:
    lines = data.split(b'\n')
    fout.write(lines[-1] + b''.join(reversed(buff)) + b'\n')
    for l in lines[-2::-1]:
        fout.write(l+b'\n')
fout.close()


