#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
sys.path.insert(0, "./leap") # load leap motion lib
import Leap
from rps_listener import RpsListener
from rps_thread import RpsThread

def main():
    th = RpsThread()
    th.start()

    time.sleep(1)
    print("さいしょは")
    time.sleep(1)
    print("グー")
    time.sleep(1)
    # 測定
    th.start_measure()

    print("じゃんけん")
    time.sleep(1)
    th.stop_measure()
    print("ほい！")

    th.join()

if __name__ == "__main__":
    main()
