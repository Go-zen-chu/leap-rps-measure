#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "./leap") # load leap motion lib
import os
from datetime import datetime
import pickle

import Leap
from Leap import Vector
from logging import getLogger, FileHandler, Formatter, DEBUG

class RpsListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    origin = Vector(0,0,0)
    logger = None
    is_measuring = False
    data_dir_path = ""

    def on_init(self, controller):
        print("Initialized")
        self.logger = getLogger(__name__)
        self.logger.setLevel(DEBUG)
        fh = FileHandler(filename=__name__ + ".tsv")
        fm = Formatter("%(asctime)s\t%(message)s")
        fh.setLevel(DEBUG)
        fh.setFormatter(fm)
        self.logger.addHandler(fh)
        self.logger.propagate = False
        # hand data = 6
        data_types = ["hand_type","hand_id","hand_confidence","palm_x","palm_y","palm_z"]
        # fingers = 5 * (2 + 12) = 70
        for f in self.finger_names:
            # length and width are decided when your hand is first detected (static)
            data_types.extend(["{}_{}".format(f, t) for t in ["len", "width"]])
            # finger bones
            for b in range(0, 4):
                data_types.extend(["{}_{}_{}".format(f, b, t) for t in ["x","y","z"]])
        data_col = "\t".join(data_types)
        self.logger.info(data_col)

    def on_connect(self, controller):
        print("Connected")

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, controller):
        print("Exited")

    def start_measure(self):
        from datetime import datetime
        now = datetime.now()
        now_str = now.strftime("%Y%m%d%H%M%S%f")
        data_dir_path = os.path.abspath("data/{}".format(now_str))
        os.makedirs(data_dir_path)
        self.data_dir_path = data_dir_path
        self.is_measuring = True

    def stop_measure(self):
        self.is_measuring = False

    def on_frame(self, controller):
        if self.is_measuring == False:
            return
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        # print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
        #       frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

        # Get hands
        if len(frame.hands) == 0:
            print("No data in this frame")
            return
        # use first hand
        hand = frame.hands[0]
        now_str = datetime.now().strftime("%Y%m%d-%H%M%S%f")
        pkl_path = os.path.join(self.data_dir_path, "{}.pkl".format(now_str))
        with open(pkl_path, 'wb') as f:
            pickle.dump(hand, f)

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"
