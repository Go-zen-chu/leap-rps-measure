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
    finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    xyz = ["x", "y", "z"]
    origin = Vector(0,0,0)
    logger = None
    log_filename = ""
    header_len = 0
    is_measuring = False
    data_dir_path = ""

    def on_init(self, controller):
        print("Initialized")

    def on_connect(self, controller):
        print("Connected")

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, controller):
        print("Exited")

    def init_logger(self, log_filename):
        now = datetime.now()
        now_str = now.strftime("%Y%m%d-%H%M%S%f")
        data_dir_path = os.path.abspath("data/{}".format(now_str))
        os.makedirs(data_dir_path)
        self.data_dir_path = data_dir_path

        self.log_filename = log_filename
        # initialize logger
        self.logger = self.setup_logger(self.data_dir_path, self.log_filename)
        data_header = self.create_data_header()
        data_header_str = "\t".join(data_header)
        self.header_len = len(data_header)
        # write header of tsv
        self.logger.info(data_header_str)

    def setup_logger(self, data_dir_path, log_filename, level=DEBUG):
        logger = getLogger(__name__)
        logger.setLevel(level)
        # create log in tsv
        fh = FileHandler(filename="{}/{}.tsv".format(data_dir_path, log_filename))
        fm = Formatter("%(asctime)s\t%(message)s")
        fh.setLevel(DEBUG)
        fh.setFormatter(fm)
        logger.addHandler(fh)
        # don't propagate to parent logger
        logger.propagate = False
        return logger

    def create_data_header(self):
        data_header = []
        # hand_header = 5
        data_header = ["hand_id", "hand_confidence"]
        data_header.extend([fng + "_angle" for fng in self.finger_names])
        return data_header

    def get_hand_data(self, hand):
        # heuristic way
        hand_data = [None] * 7
        hand_data[0] = hand.id
        hand_data[1] = hand.confidence
        idx = 2
        hand_direction = hand.direction
        palm_normal = hand.palm_normal
        for fng in hand.fingers:
            angle_hand_fng = hand_direction.angle_to(fng.direction) * 180 / math.pi
            angle_norm_fng = palm_normal.angle_to(fng.direction) * 180 / math.pi
            if angle_norm_fng > 90:
                angle_hand_fng = angle_hand_fng * -1
            hand_data[idx + fng.type] = angle_hand_fng
        return hand_data

    def start_measure(self):
        self.is_measuring = True

    def stop_measure(self):
        self.is_measuring = False

    def on_frame(self, controller):
        if self.is_measuring == False:
            return
        frame = controller.frame()
        if len(frame.hands) == 0:
            print("No data in this frame")
            return
        # use first hand
        hand = frame.hands[0]
        # they do not contain valid tracking data and do not correspond to a physical entity
        if hand.is_valid == False:
            print("Not valid hand")
            return
        hand_data = self.get_hand_data(hand)
        self.logger.info("\t".join(map(str, hand_data)))
