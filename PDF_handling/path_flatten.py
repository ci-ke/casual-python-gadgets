# 将层级文件夹展平，便于pdf补丁丁批量处理，之后再放回

# config
UNFLATTEN_ROOT = 'root'
FLATTEN_ROOT = 'flatten'
EXT = 'pdf'
SPLIT = '$$'
TASK = 'unflatten'

# code
import os
import shutil


def flatten(root: str) -> None:
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            src_path = os.path.join(dirpath, filename)
            ext = os.path.splitext(src_path)[1].lower()
            if ext == '.' + EXT:
                flat_path = src_path.replace('\\', SPLIT)
                tgt_path = os.path.join(FLATTEN_ROOT, flat_path)
                shutil.move(src_path, tgt_path)
                print(src_path + '- > ' + tgt_path)


def unflatten(root: str) -> None:
    filenames = os.listdir(root)
    for filename in filenames:
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.' + EXT:
            unflatten_path = filename.replace(SPLIT, '\\')
            src_path = os.path.join(root, filename)
            tgt_path = unflatten_path
            shutil.move(src_path, tgt_path)
            print(src_path + '- > ' + tgt_path)


def main():
    if TASK == 'flatten':
        flatten(UNFLATTEN_ROOT)
    elif TASK == 'unflatten':
        unflatten(FLATTEN_ROOT)


if __name__ == '__main__':
    main()
