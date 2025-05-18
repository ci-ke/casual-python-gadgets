import os
from typing import Any, Dict, List

from PyPDF2 import PdfReader

DIR = r'D:\书籍'


def walk(adr: str) -> List[str]:
    mylist = []
    for root, _, files in os.walk(adr):
        for name in files:
            if os.path.splitext(name)[1] == '.pdf':
                adrlist = os.path.join(root, name)
                mylist.append(adrlist)
    return mylist


def detect_not_text_or_freeText_annotation_in_file(
    filename: str,
) -> List[Dict[str, Any]]:
    collect = []
    reader = PdfReader(filename)
    for page_num, page in enumerate(reader.pages):
        page_num += 1
        if "/Annots" in page:
            for annot in page["/Annots"]:
                obj = annot.get_object()
                annotation = {
                    "page_num": page_num,
                    "subtype": obj["/Subtype"],
                    "contents": obj.get("/Contents"),
                }
                if (
                    annotation["subtype"] not in ('/Text', '/FreeText')
                    and annotation['contents'] is not None
                ):
                    collect.append(annotation)
    return collect


def detect_not_text_or_freeText_annotation_in_dir(dirname: str) -> None:
    fl = walk(dirname)

    for idx, f in enumerate(fl):
        show = f'{idx}/{len(fl)}'
        print(show, end='\r')

        collect = detect_not_text_or_freeText_annotation_in_file(f)

        print(' ' * len(show), end='\r')
        if len(collect) != 0:
            print(f)
            for i in collect:
                print(i)
            print()


if __name__ == '__main__':
    detect_not_text_or_freeText_annotation_in_dir(DIR)
