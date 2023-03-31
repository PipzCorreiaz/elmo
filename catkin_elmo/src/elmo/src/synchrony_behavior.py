#! /usr/bin/env python3


import random
import rospy
import robot as r
from std_msgs.msg import String
import time


MIN_SLEEP = 2.0
MAX_SLEEP = 4.0


class Node:

    def __init__(self):
        self.pan_tilt_api = r.PanTilt()
        self.server_api = r.Server()
        self.onboard_api = r.Onboard()
        self.enabled = False
        rospy.set_param("behaviour/synchrony_behaviour/enabled", self.enabled)
        rospy.Subscriber("behaviour/enable", String, self.on_enable)
        rospy.Subscriber("behaviour/disable", String, self.on_disable)

    def on_enable(self, msg):
        if msg.data != "synchrony_behaviour" or self.enabled:
            return
        print("enabling test motors")
        self.pan_tilt_api.enable(True, True)
        self.pan_tilt_api.reset_angles()
        self.enabled = True
        rospy.set_param("behaviour/synchrony_behaviour/enabled", self.enabled)

    def on_disable(self, msg):
        if msg.data != "synchrony_behaviour" or not self.enabled:
            return
        print("disabling test motors")
        self.enabled = False
        self.pan_tilt_api.reset_angles()
        rospy.sleep(2.0)
        self.pan_tilt_api.enable(False, False)
        rospy.set_param("behaviour/synchrony_behaviour/enabled", self.enabled)

    

    def gaze(self, pan, tilt, duration, freq, move):
        rate = rospy.Rate(10)
        start_time = time.time()
        status = self.pan_tilt_api.get_status()
        init_pan = status["pan_angle"]
        init_tilt = status["tilt_angle"]
        print("init pan=" + str(init_pan) + ", tilt=" + str(init_tilt))
        
        size = (duration / 1000) * freq
        sleep_duration = 1 / freq
        i = 0

        delta_pan = (pan - init_pan) / size
        delta_tilt = (tilt - init_tilt) / size
        while i < size:
            p = init_pan + (i + 1) * delta_pan
            t = init_tilt + (i + 1) * delta_tilt
            self.pan_tilt_api.set_angles(pan=p, tilt=t, playtime=200)
            print("command pan=" + str(p) + ", tilt=" + str(t))
            i += 1
            time.sleep(sleep_duration)
        
        end_time = time.time()
        print("Duration: " + str(end_time - start_time))
        time.sleep(2)
        status = self.pan_tilt_api.get_status()
        print("current pan=" + str(status["pan_angle"]) + ", tilt=" + str(status["tilt_angle"]))


    def synchrony(self):
        rate = rospy.Rate(10)
        print("Starting Synchronous Behaviour")
       
        OBJECT = {'pan': 80, 'tilt': 15, 'target': 'Object'}
        PERSON = {'pan': 80, 'tilt': -5, 'target': 'Person'}
        gazes = [OBJECT, PERSON, OBJECT, PERSON, OBJECT, PERSON, OBJECT]
        duration = [2.0, 2.0, 2.0, 1.0, 1.0, 0.5, 0.5]
        wait_after_gaze = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0]
        i = 0        
        while i < len(gazes):
            p = gazes[i]['pan']
            t = gazes[i]['tilt']
            self.pan_tilt_api.set_angles(pan=p, tilt=t, playtime= duration[i])
            print("Gazing at " + gazes[i]['target'])
            time.sleep(duration[i] + wait_after_gaze[i])
            i += 1
        print("Finished Synchronous Behaviour")


if __name__ == '__main__':
    rospy.init_node("synchrony_behaviour")
    NODE = Node()
    rospy.loginfo("synchrony_behaviour: running")
    NODE.synchrony()    
    #NODE.run()

