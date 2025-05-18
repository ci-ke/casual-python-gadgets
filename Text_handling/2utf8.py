import os
import sys
from chardet import detect

root = sys.argv[1]
postfix = sys.argv[2]  # .txt


def convert_to_utf8(filename: str) -> None:
    with open(filename, 'rb') as f:
        s = f.read()
    coding = detect(s)['encoding']
    os.remove(filename)
    with open(filename, 'wb') as f:
        f.write(s.decode(coding).encode('utf8'))


if __name__ == '__main__':
    for rt, dirs, files in os.walk(root):
        for f in files:
            print(f)
            fname = os.path.splitext(f)
            print(fname[1])
            if fname[1] == postfix:
                print(rt + '\\' + f)
                convert_to_utf8(rt + '\\' + f)
