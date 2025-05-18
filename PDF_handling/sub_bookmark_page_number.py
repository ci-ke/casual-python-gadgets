# 将sys.argv[1]文件的行末数字减去sys.argv[2]

import sys, os

input_file = sys.argv[1]
number = int(sys.argv[2])

f = open(input_file, encoding='utf-8')
for line in f.readlines():
    keep = line[: line.rindex('\t') + 1]
    page = int(line[line.rindex('\t') + 1 :])
    new_page = page - number
    new_line = keep + str(new_page)
    print(new_line)
