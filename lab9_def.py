# Предложение с максимальным числом гласных букв.

current_text = [
    'Обучение в МГТУ им. Н.Э. Баумана ведется на 10+9 факультетах дневного обучения. Работает, аспирантура и',
    'докторантура, два профильных лицея.МГТУ им. Н.Э. Баумана осуществляет подготовку более 19 тысяч',
    'студентов практически по всему спектру современного машино- и приборостроения. Научную и учебную работу',
    '    ведут более 320 докторов и около 2000-199+7+-8+200 кандидатов наук. Основными структурными подразделениями',
    'Бауманского университета являются научно-учебные комплексы, имеющие в своем составе факультет и',
    'научно-исследовательский институт. Их — восемь (см. в колонке справа). ~амяв   - , о ж.',
    'АБАБАБ АБ А Б А. АААББА. АА',
    # 'оаиоаиоаоиоаоиоаоиоаоиоеееееееееееееееаоиоаоиоаоиоаоаиаеуиаооиыауеиаыуениаеыуаиыуааеыуаи'
]

vowel = {'а', 'я', 'о', 'е', 'у', 'ю', 'ы', 'и', 'э', 'ё'}  # Список гласных букв

res = []

mx_sentence = []
mx_vowel_cnt = 0

sentence = []
vowel_cnt = 0
for l in current_text:
    for i in l:
        sentence.append(i)
        if i.lower() in vowel:
            vowel_cnt += 1
        elif i == '.':
            if vowel_cnt > mx_vowel_cnt:
                mx_vowel_cnt = vowel_cnt
                mx_sentence = sentence.copy()
            res.append((vowel_cnt, sentence.copy()))
            sentence.clear()
            vowel_cnt = 0
    if vowel_cnt > mx_vowel_cnt:
        mx_vowel_cnt = vowel_cnt
        mx_sentence = sentence.copy()
    res.append((vowel_cnt, sentence.copy()))
    sentence.append(' ')

print(''.join(mx_sentence))
print(mx_vowel_cnt)
for i in res:
    print(i)
