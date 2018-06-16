#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "./leap") # load leap motion lib
import threading

import Leap
from rps_listener import RpsListener

class RpsThread(threading.Thread):
    # init 時に渡さないと thread run してからは別のメモリ
    def __init__(self):
        super(RpsThread, self).__init__()
        self.name = "rps_thread"
        self.listener = RpsListener()
        self.controller = Leap.Controller()

    def run(self):
        print("start rps thread")
        self.controller.add_listener(self.listener)

    def join(self):
        self.controller.remove_listener(self.listener)

    def start_measure(self):
        self.listener.start_measure()

    def stop_measure(self):
        self.listener.stop_measure()
