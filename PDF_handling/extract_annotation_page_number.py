# sys.argv[1]为“导出所有注释到数据文件”的文件，提取前要把逻辑页码清空

import sys

pages = set()
with open(sys.argv[1], 'rb') as f:
    context = f.read()
    j = -1
    while True:
        i = context.find(b'/Page ', j + 1)
        if i == -1:
            break
        j = context.find(b'/', i + 1)
        pages.add(int(context[i + 6 : j]) + 1)

pages = sorted(pages)
pages = [str(x) for x in pages]
print(','.join(pages))
