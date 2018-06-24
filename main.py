#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
sys.path.insert(0, "./leap") # load leap motion lib
import Leap
from rps_listener import RpsListener
from rps_thread import RpsThread

def main():
    listener = RpsListener()
    listener.init_logger("gu")
    controller = Leap.Controller()
    controller.add_listener(listener)

    time.sleep(1)
    print("さいしょは")
    time.sleep(1)
    print("グー")
    time.sleep(1)
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
