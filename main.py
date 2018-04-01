#!/usr/bin/env python
import sys, thread, time
sys.path.insert(0, "./leap") # load leap motion lib

import Leap
from rps_listener import RpsListener

def main():
    listener = RpsListener()
    controller = Leap.Controller()
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        controller.remove_listener(listener)

if __name__ == "__main__":
    main()
