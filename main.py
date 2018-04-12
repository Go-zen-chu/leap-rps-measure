#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, thread, time
sys.path.insert(0, "./leap") # load leap motion lib

import Leap
from rps_listener import RpsListener, RpsThread
from opengl import OpenGLWindow
import Queue

def main():
    # data for inter-thread
    stack = Queue.LifoQueue(1) # length is 1 (put only last data)
    th = RpsThread(stack)
    th.start()
    # has to be called in main thread
    w = OpenGLWindow(b"leap rps", 800, 600)
    w.set_data_stack(stack)
    w.start_window()

if __name__ == "__main__":
    main()
