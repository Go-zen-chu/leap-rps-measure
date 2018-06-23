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
    header_len = 0
    is_measuring = False
    data_dir_path = ""

    def on_init(self, controller):
        print("Initialized")
        now = datetime.now()
        now_str = now.strftime("%Y%m%d-%H%M%S%f")
        data_dir_path = os.path.abspath("data/{}".format(now_str))
        os.makedirs(data_dir_path)
        self.data_dir_path = data_dir_path

        # initialize logger
        self.logger = self.setup_logger()
        data_header = self.create_data_header()
        data_header_str = "\t".join(data_header)
        self.header_len = len(data_header)
        # write header of tsv
        self.logger.info(data_header_str)

    def on_connect(self, controller):
        print("Connected")

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, controller):
        print("Exited")

    def setup_logger(self):
        logger = getLogger(__name__)
        logger.setLevel(DEBUG)
        # create log in tsv
        fh = FileHandler(filename="{}/{}.tsv".format(self.data_dir_path,__name__))
        fm = Formatter("%(asctime)s\t%(message)s")
        fh.setLevel(DEBUG)
        fh.setFormatter(fm)
        logger.addHandler(fh)
        # don't propagate to parent logger
        logger.propagate = False
        return logger

    def create_data_header(self):
        data_header = []
        # hand_header = 7 + 3*3 = 16
        hand_header = ["hand_type","hand_id","hand_confidence","palm_x","palm_y","palm_z","palm_width"]
        for bs in ["x_basis", "y_basis", "z_basis"]:
            hand_header.extend(["hand_{}_{}".format(bs, ax) for ax in self.xyz])
        # finger_header = 5 * (2 + 3 + 3 + 4*3) = 100
        finger_header = []
        for f in self.finger_names:
            # length and width are decided when your hand is first detected (static)
            finger_header.extend(["{}_{}".format(f, t) for t in ["len", "width"]])
            finger_header.extend(["{}_direction_{}".format(f, ax) for ax in self.xyz])
            finger_header.extend(["{}_velocity_{}".format(f, ax) for ax in self.xyz])
            # finger bones, all fingers contain 4 bones
            for b in range(0, 4):
                finger_header.extend(["{}_{}_center_{}".format(f, b, ax) for ax in self.xyz])
        data_header.extend(hand_header)
        data_header.extend(finger_header)
        return data_header

    def get_hand_data(self, hand):
        # fast array initializaion
        d = [None] * self.header_len
        d[0] = "L" if hand.is_left else "R"
        d[1] = hand.id
        d[2] = hand.confidence
        pp = hand.palm_position
        d[3] = pp.x
        d[4] = pp.y
        d[5] = pp.z
        d[6] = hand.palm_width
        idx = 7
        basis = hand.basis
        for bs in [basis.x_basis, basis.y_basis, basis.z_basis]:
            for val in [bs.x, bs.y, bs.z]:
                d[idx] = val
                idx += 1
        for fng in hand.fingers:
            d[idx] = fng.length
            idx +=1
            d[idx] = fng.width
            idx +=1
            fng_dir = fng.direction
            fng_vel = fng.tip_velocity
            for val in [fng_dir.x, fng_dir.y, fng_dir.z]:
                d[idx] = val
                idx += 1
            for val in [fng_vel.x, fng_vel.y, fng_vel.z]:
                d[idx] = val
                idx += 1
            for b in range(0, 4):
                bn = fng.bone(b)
                d[idx] = bn.center.x
                idx += 1
                d[idx] = bn.center.y
                idx += 1
                d[idx] = bn.center.z
                idx += 1
        return d

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
