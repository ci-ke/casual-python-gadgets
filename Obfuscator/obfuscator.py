# use this on https://pyob.oxyry.com/ (browser window maximum)
# obfuscator.png is the small screenshot of "OBFUSCATE" button
# requirements: pyautogui pyperclip pillow opencv-python

import os, sys, time, tkinter, argparse
import os.path as op
import pyautogui
import pyperclip


# constant
EXT = 'py'
SAVEDIR_TAIL = '_obfuscated'
MATCH_PIC = 'obfuscator.png'
WAITING_TIME = 2

# variable
BASEDIR = ''
SAVEDIR = ''
WIDTH, HEIGHT = pyautogui.size()


class LongRet(Exception):
    pass


def use_webpage() -> None:
    script_dir_path = op.split(op.realpath(__file__))[0]
    button = pyautogui.locateOnScreen(
        op.join(script_dir_path, MATCH_PIC), confidence=0.9
    )
    if button is None:
        label.config(text='can\'t find OBFUSCATE button in current window')
        raise LongRet
    else:
        pyautogui.click(0.25 * WIDTH, 0.5 * HEIGHT)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.typewrite(['backspace'])
        pyautogui.hotkey('ctrl', 'v')

        button = pyautogui.locateOnScreen(
            op.join(script_dir_path, MATCH_PIC), confidence=0.9
        )
        pyautogui.click(pyautogui.center(button))
        time.sleep(WAITING_TIME)

        pyautogui.click(0.75 * WIDTH, 0.5 * HEIGHT)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')


def write_file(tgt_content: str, tgt_path: str) -> bool:
    if tgt_content.find('# Loading') == 0:
        return False

    open(tgt_path, 'w').write(tgt_content)
    return True


def read_file() -> None:
    if op.isdir(SAVEDIR):
        label.config(text='save folder already exsist')
        raise LongRet
    else:
        os.mkdir(SAVEDIR)

    first_time = True
    for dirpath, _, filenames in os.walk(BASEDIR):
        if dirpath == SAVEDIR:
            continue

        for filename in filenames:
            ext = op.splitext(filename)[1].lower()
            if ext == '.' + EXT:
                break
        else:
            continue

        if not first_time:
            savedir = op.join(SAVEDIR, op.basename(dirpath))
            if not op.isdir(savedir):
                os.mkdir(savedir)
        else:
            savedir = SAVEDIR
        first_time = False

        for filename in filenames:
            ext = op.splitext(filename)[1].lower()
            if ext == '.' + EXT:
                src_path = op.join(dirpath, filename)
                tgt_path = op.join(savedir, filename)
                src_content = open(src_path, 'r').read().replace('\r\n', '\n')

                while True:
                    pyperclip.copy(src_content)
                    use_webpage()
                    tgt_content = pyperclip.paste().replace('\r\n', '\n')

                    if tgt_content.find('# Syntax error: invalid syntax') == 0:
                        tgt_content = src_content
                        print(src_path + ' -> ' + tgt_path + ' unmodified')

                    if write_file(tgt_content, tgt_path):
                        break


def parse_args() -> None:
    global BASEDIR, SAVEDIR

    parser = argparse.ArgumentParser()
    parser.add_argument('project_dir')
    parser.add_argument('save_in_dir')
    args = parser.parse_args()

    if op.isdir(args.project_dir):
        BASEDIR = op.abspath(args.project_dir)
    else:
        sys.exit(print('arg 1 (project_dir) must be a dir'))

    if op.isdir(args.save_in_dir):
        SAVEDIR = op.abspath(
            op.join(args.save_in_dir, op.basename(BASEDIR) + SAVEDIR_TAIL)
        )
    else:
        sys.exit(print('arg 2 (save_in_dir) must be a dir'))


def run() -> None:
    try:
        root.title('working...')
        label.config(text='working...')
        read_file()
        label.config(text='done')
        root.title('done')
    except LongRet:
        root.title('pause')
        return


if __name__ == '__main__':
    parse_args()
    root = tkinter.Tk()
    root.geometry("300x100")
    tkinter.Button(root, text="Run", command=run).pack()
    label = tkinter.Label(root, text='Ready')
    label.pack()
    root.mainloop()
