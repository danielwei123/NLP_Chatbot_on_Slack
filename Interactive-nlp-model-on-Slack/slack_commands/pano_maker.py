#!/usr/bin/env python

from __future__ import print_function
import sys
import rospy
import cv2
import os
from std_msgs.msg import String
from sensor_msgs.msg import CompressedImage
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist
import argparse
import numpy as np
import json
import requests
import stitching_functions
import os
import glob
import time

PI = 3.1415926535897

class Panorama:
    def __init__(self):

        # rospy.init_node('take_photo', anonymous=False)
        self.bridge = CvBridge()
        self.image_received = False

        # Connect image topic
        img_topic = "/raspicam_node/image/compressed"
        self.image_sub = rospy.Subscriber(img_topic, CompressedImage, self.callback)
        self.velocity_publisher = rospy.Publisher('cmd_vel', Twist, queue_size=10)
        self.angular = 0
        self.vel_sub = rospy.Subscriber('cmd_vel', Twist, self.getVelocity, queue_size=10)

        self.image = None
        self.location = "testarino/"



        # Allow up to one second to connection
        rospy.sleep(1)


    def rotate(self):
        #Starts a new node
        vel_msg = Twist()

        # Receiveing the user's input
        print("Let's rotate your robot")
        speed = 8
        angle = 352
        clockwise = True
        current_angle = 0
        count = 0

        #Converting from angles to radians
        angular_speed = speed*2*PI/360
        relative_angle = angle*2*PI/360

        #We wont use linear components
        vel_msg.linear.x=0
        vel_msg.linear.y=0
        vel_msg.linear.z=0
        vel_msg.angular.x = 0
        vel_msg.angular.y = 0

        # Checking if our movement is CW or CCW
        vel_msg.angular.z = -abs(angular_speed)
        self.velocity_publisher.publish(vel_msg)
        # Setting the current time for distance calculus
        t0 = time.time()
        while(current_angle <= relative_angle):
            t1 = time.time()
            current_angle = angular_speed*(t1-t0)
            if int(current_angle * (180/PI)) >= count:
                self.save_file(name = int(current_angle * (180/PI)), img = self.image)
                count += 22
        #Forcing our robot to stop
        vel_msg.linear.x=0
        vel_msg.linear.y=0
        vel_msg.linear.z=0
        vel_msg.angular.x = 0
        vel_msg.angular.y = 0
        vel_msg.angular.z = 0
        self.velocity_publisher.publish(vel_msg)

    def getVelocity(self, data):
        self.angular = data.angular.z

    def callback(self, data):
        # Convert image to OpenCV format
        try:
            cv_image = self.bridge.compressed_imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        self.image_received = True
        self.image = cv_image

    def stitch_images(self):
        panorama = stitching_functions.binary_image_stitcher(self.location)
        self.save_file(name = "pano_image", img =  panorama)

    def save_file(self, name, img):
        if name == 0: #dunno tbh, this always saves a blank image
            return None
        img_title = str(name) + ".jpg"
        if not os.path.exists(self.location): #make a directory for the images if it doesnt exist
            os.makedirs(self.location)
        cv2.imwrite(self.location + img_title, img)

    def reinit_directory(self):
        files = glob.glob(self.location + "*")
        for f in files:
            os.remove(f)

if __name__ == '__main__':
    # Initialize
    #TakePhoto()
    camera = Panorama()
    camera.reinit_directory() #remove in prod

    # Begins photo series
    camera.take_pictures()
    camera.stitch_images()

    #Sleep to give the last log messages time to be sent
    rospy.sleep(.4)