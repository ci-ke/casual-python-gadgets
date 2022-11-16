# config
level = [0] * 4
start = '前言'  # 第一章
end = 'Bibliography'  # 不再处理的章节

# code
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('FreePic2Pdf_bkmk.txt', encoding='utf-16le') as f:
    last_level = 0
    start_handle = False

    for line in f:
        if line[: len(start)] == start:
            start_handle = True
        if line[: len(end)] == end:
            start_handle = False
        if not start_handle:
            print(line, end='')
            continue

        this_level = 0
        for char in line:
            if char == '\t':
                this_level += 1
            else:
                break

        if this_level < last_level:
            level[this_level + 1 :] = [0] * (len(level) - (this_level + 1))
        level[this_level] += 1
        last_level = this_level

        print(
            '\t' * this_level
            + '.'.join(map(str, level[: this_level + 1]))
            + ' '
            + line[this_level:],
            end='',
        )
