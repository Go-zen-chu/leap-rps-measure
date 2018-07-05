#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
sys.path.insert(0, "./leap") # load leap motion lib
import Leap
from rps_listener import RpsListener
from rps_thread import RpsThread

def main():
    num_args = len(sys.argv)
    if num_args != 2:
        sys.exit("Insufficient args. usage) main.py rock")
    rps = sys.argv[1] # measuring rock, paper, or scissors
    listener = RpsListener()
    listener.init_logger(rps)
    controller = Leap.Controller()
    controller.add_listener(listener)

    time.sleep(1)
    print("さいしょは")
    time.sleep(0.5)
    print("グー")
    time.sleep(0.5)
    # 測定
    listener.start_measure()

    print("じゃんけん")
    time.sleep(1)
    # 停止
    listener.stop_measure()

    print("ほい！")

    controller.remove_listener(listener)

if __name__ == "__main__":
    main()
