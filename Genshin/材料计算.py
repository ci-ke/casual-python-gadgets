import tkinter
from typing import List, Tuple


def process_input(in_str: str) -> Tuple[str, List[int]]:
    in_str_list = in_str.split()
    try:
        in_list = [int(x) for x in in_str_list]
    except ValueError:
        return '输入类型有误', []
    if len(in_list) != 5:
        return '输入个数有误', []
    negative_error = False
    for x in in_list:
        if x < 0:
            negative_error = True
            break
    if negative_error:
        return '不能为负数', []
    in_list.reverse()
    return '', in_list


def calculate_diff(result: List[int], target: List[int]) -> List[int]:
    diff = []
    for re, ta in zip(result, target):
        diff.append(0 if re >= ta else ta - re)
    return diff


def process_output(output: List[int]) -> str:
    return str(list(reversed(output)))[1:-1]


def judge_result(result: List[int], target: List[int]) -> bool:
    for re, ta in zip(result, target):
        if re < ta:
            return False
    return True


def calculate() -> None:
    have_str = e1.get()
    target_str = e2.get()

    flag, have = process_input(have_str)
    if len(flag) != 0:
        lb3["text"] = flag
        return
    flag, target = process_input(target_str)
    if len(flag) != 0:
        lb3["text"] = flag
        return

    need = []
    for ta, ha in zip(target, have):
        need.append(ta - ha)
    for i in range(len(need)):
        if need[i] > 0:
            for j in range(i - 1, -1, -1):
                if need[j] < 0:
                    most_convert = int((-need[j]) / (3 ** (i - j)))
                    if most_convert >= need[i]:
                        consume = need[i] * (3 ** (i - j))
                        need[i] = 0
                        have[i] = target[i]
                        need[j] += consume
                        have[j] -= consume
                    else:
                        consume = most_convert * (3 ** (i - j))
                        need[i] -= most_convert
                        have[i] += most_convert
                        need[j] += consume
                        have[j] -= consume
                if need[i] == 0:
                    break
                assert not need[i] < 0

    result = have
    diff = calculate_diff(result, target)

    result_str = '{0:{1}<21}{2}\n'.format(
        '转换结果（五星 四星 三星 二星 一星）：', chr(12288), process_output(result)  # chr(12288):中文空格
    )
    result_str += '{0:{1}<21}{2}\n'.format(
        '还差（五星 四星 三星 二星 一星）：', chr(12288), process_output(diff)
    )
    result_str += '已经刷够了\n' if judge_result(result, target) else '还得继续刷\n'

    lb3["text"] = result_str


if __name__ == '__main__':

    baseFrame = tkinter.Tk()
    baseFrame.title('材料计算')

    lb1 = tkinter.Label(baseFrame, text="输入拥有个数（五星 四星 三星 二星 一星）（不存在则填0）：")
    lb1.grid(row=0, column=0, stick=tkinter.W)

    e1 = tkinter.Entry(baseFrame)
    e1.grid(row=0, column=1, stick=tkinter.E)

    lb2 = tkinter.Label(baseFrame, text="输入目标个数（五星 四星 三星 二星 一星）（不存在则填0）：")
    lb2.grid(row=1, column=0, stick=tkinter.W)

    e2 = tkinter.Entry(baseFrame)
    e2.grid(row=1, column=1, stick=tkinter.E)

    btn = tkinter.Button(baseFrame, text="计算", command=calculate)
    btn.grid(row=2, column=1, stick=tkinter.E)

    lb3 = tkinter.Label(baseFrame, text="", justify=tkinter.LEFT)
    lb3.grid(row=3)

    baseFrame.mainloop()
