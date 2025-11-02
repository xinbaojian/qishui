import sys
from qishui import qishui_ad
from screen import un_lock


if __name__ == '__main__':
    un_lock()
    if len(sys.argv) > 1:
        if sys.argv[1] == 'qishui':
            qishui_ad()
        if sys.argv[1] == 'xima':
            print("xiaomi ad")
    else:
        print("使用方法: python3 main.py qishui")