#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "./leap") # load leap motion lib
import thread
import time
import math

import Leap
from Leap import Vector
from logging import getLogger, FileHandler, Formatter, DEBUG

class RpsListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    origin = Vector(0,0,0)
    logger = None

    def on_init(self, controller):
        print "Initialized"
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
        print "Connected"

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def log_hand_data(self, hand, finger_data):
        # fast array initializaion
        d = [None] * 76
        d[0] = "L" if hand.is_left else "R"
        d[1] = hand.id
        d[2] = hand.confidence
        pp = hand.palm_position
        d[3] = pp.x
        d[4] = pp.y
        d[5] = pp.z

        idx = 6
        for f in finger_data:
            if f is None:
                idx += 14
                continue
            d[idx] = f.length
            idx += 1
            d[idx] = f.width
            idx += 1
            for b in range(0, 4):
                bone = f.bone(b)
                d[idx] = bone.center.x
                idx += 1
                d[idx] = bone.center.y
                idx += 1
                d[idx] = bone.center.z
                idx += 1

        # map to convert to str array
        self.logger.info("\t".join(map(str,d)))

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        # print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
        #       frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

        # Get hands
        for hand in frame.hands:
            handType = "Left hand" if hand.is_left else "Right hand"
            print "  %s, id %d, position: %s, conf: %f" % (
                handType, hand.id, hand.palm_position, hand.confidence)

            # Get the hand's normal vector and direction
            # normal = hand.palm_normal
            # direction = hand.direction

            # Calculate the hand's pitch, roll, and yaw angles
            # print "  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
            #     direction.pitch * Leap.RAD_TO_DEG,
            #     normal.roll * Leap.RAD_TO_DEG,
            #     direction.yaw * Leap.RAD_TO_DEG)
            hand_center = hand.palm_position
            hand_direction = hand.direction
            # hand_center_len = hand_center.distance_to(self.origin)
            # Get fingers
            finger_data = [None] * 5
            tip_dists = [0] * 5
            tip_angles = [0] * 5
            for finger in hand.fingers:
                finger_data[finger.type] = finger
                # dist between center and finger tip
                tip_palm_dist = finger.bone(3).center.distance_to(hand_center)
                tip_dists[finger.type] = tip_palm_dist
                tip_angles[finger.type] = finger.bone(3).direction.angle_to(hand_direction) * 180 / math.pi
                # print "    %s finger, id: %d, length: %fmm, width: %fmm" % (
                #     self.finger_names[finger.type],
                #     finger.id,
                #     finger.length,
                #     finger.width)
                # # Get bones
                # for b in range(0, 4):
                #     bone = finger.bone(b)
                #     print "      Bone: %s, start: %s, end: %s, direction: %s" % (
                #         self.bone_names[bone.type],
                #         bone.prev_joint,
                #         bone.next_joint,
                #         bone.direction)
            print(tip_dists)
            print(tip_angles)
            # if all([d >  for d in tip_dists]):
            #     print("パー")
            # elif all([d < 70 for d in tip_dists]):
            #     print("グー")
            # elif tip_dists[0] < 70 and tip_dists[1] > 75 and tip_dists[2] > 75 and tip_dists[3] < 70 and tip_dists[4] < 70:
            #     print("チョキ")
            # else:
            #     print("それ以外")

            # log data for analysis
            self.log_hand_data(hand, finger_data)

        if not (frame.hands.is_empty and frame.gestures().is_empty):
            print ""

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"
