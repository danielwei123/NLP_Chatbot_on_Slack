#!/usr/bin/env python

import roslib
import rospy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import BatteryState, CompressedImage, Range
from std_msgs.msg import String 
from cv_bridge import CvBridge, CvBridgeError
import cv2
import datetime
import math


class RoboInfo():

    def __init__(self, index):
        rospy.init_node('slack_node', anonymous=False) #initialize node for ROS

        if index == '1':
            #Velocity readings
            self.current_angle = 0
            self.current_velocity = 0
            self.vel_sub = rospy.Subscriber('bot1/cmd_vel', Twist, self.getVelocity, queue_size=1)
            self.cmd_vel = rospy.Publisher('bot1/cmd_vel', Twist, queue_size=1)
            self.old_velocity = None


            #Battery readings
            self.current_voltage = 0
            self.batt_sub = rospy.Subscriber('bot1/battery_state', BatteryState, self.getBattery, queue_size=1)


            #Camera view
            self.image = None
            self.bridge = CvBridge()
            self.image_sub = rospy.Subscriber('bot1/raspicam_node/image/compressed', CompressedImage, self.getImage, queue_size=1)

            # #Time readings
            # self.time = rospy.get_rostime()

            #Sensor readings
            self.distance_f = 0
            self.distance_b = 0
            self.sensor_f_sub = rospy.Subscriber('bot1/sonar_f', Range, self.getSonar_f, queue_size=1)
            self.sensor_b_sub = rospy.Subscriber('bot1/sonar_b', Range, self.getSonar_b, queue_size=1)

            #Panoramic trigger
            self.pano_pub = rospy.Publisher("bot1/pano_state", String, queue_size=3)     
            rospy.sleep(50)
            self.pano_pub.publish(String("False"))

            rospy.on_shutdown(self.shutdown)

        if index == '2':
            #Velocity readings
            self.current_angle = 0
            self.current_velocity = 0
            self.vel_sub = rospy.Subscriber('bot2/cmd_vel', Twist, self.getVelocity, queue_size=1)
            self.cmd_vel = rospy.Publisher('bot2/cmd_vel', Twist, queue_size=1)
            self.old_velocity = None


            #Battery readings
            self.current_voltage = 0
            self.batt_sub = rospy.Subscriber('bot2/battery_state', BatteryState, self.getBattery, queue_size=1)


            #Camera view
            self.image = None
            self.bridge = CvBridge()
            self.image_sub = rospy.Subscriber('bot2/raspicam_node/image/compressed', CompressedImage, self.getImage, queue_size=1)

            # #Time readings
            # self.time = rospy.get_rostime()

            #Sensor readings
            self.distance_f = 0
            self.distance_b = 0
            self.sensor_f_sub = rospy.Subscriber('bot2/sonar_f', Range, self.getSonar_f, queue_size=1)
            self.sensor_b_sub = rospy.Subscriber('bot2/sonar_b', Range, self.getSonar_b, queue_size=1)

            #Panoramic trigger
            self.pano_pub = rospy.Publisher("bot2/pano_state", String, queue_size=3)     
            rospy.sleep(50)
            self.pano_pub.publish(String("False"))

            rospy.on_shutdown(self.shutdown)

        if index == '3':
            #Velocity readings
            self.current_angle = 0
            self.current_velocity = 0
            self.vel_sub = rospy.Subscriber('bot3/cmd_vel', Twist, self.getVelocity, queue_size=1)
            self.cmd_vel = rospy.Publisher('bot3/cmd_vel', Twist, queue_size=1)
            self.old_velocity = None


            #Battery readings
            self.current_voltage = 0
            self.batt_sub = rospy.Subscriber('bot3/battery_state', BatteryState, self.getBattery, queue_size=1)


            #Camera view
            self.image = None
            self.bridge = CvBridge()
            self.image_sub = rospy.Subscriber('bot3/raspicam_node/image/compressed', CompressedImage, self.getImage, queue_size=1)

            # #Time readings
            # self.time = rospy.get_rostime()

            #Sensor readings
            self.distance_f = 0
            self.distance_b = 0
            self.sensor_f_sub = rospy.Subscriber('bot3/sonar_f', Range, self.getSonar_f, queue_size=1)
            self.sensor_b_sub = rospy.Subscriber('bot3/sonar_b', Range, self.getSonar_b, queue_size=1)

            #Panoramic trigger
            self.pano_pub = rospy.Publisher("bot3/pano_state", String, queue_size=3)     
            rospy.sleep(50)
            self.pano_pub.publish(String("False"))

            rospy.on_shutdown(self.shutdown)

        if index == '4':
            #Velocity readings
            self.current_angle = 0
            self.current_velocity = 0
            self.vel_sub = rospy.Subscriber('bot4/cmd_vel', Twist, self.getVelocity, queue_size=1)
            self.cmd_vel = rospy.Publisher('bot4/cmd_vel', Twist, queue_size=1)
            self.old_velocity = None


            #Battery readings
            self.current_voltage = 0
            self.batt_sub = rospy.Subscriber('bot4/battery_state', BatteryState, self.getBattery, queue_size=1)


            #Camera view
            self.image = None
            self.bridge = CvBridge()
            self.image_sub = rospy.Subscriber('bot4/raspicam_node/image/compressed', CompressedImage, self.getImage, queue_size=1)

            # #Time readings
            # self.time = rospy.get_rostime()

            #Sensor readings
            self.distance_f = 0
            self.distance_b = 0
            self.sensor_f_sub = rospy.Subscriber('bot4/sonar_f', Range, self.getSonar_f, queue_size=1)
            self.sensor_b_sub = rospy.Subscriber('bot4/sonar_b', Range, self.getSonar_b, queue_size=1)

            #Panoramic trigger
            self.pano_pub = rospy.Publisher("bot4/pano_state", String, queue_size=3)     
            rospy.sleep(50)
            self.pano_pub.publish(String("False"))

            rospy.on_shutdown(self.shutdown)

    def takePano(self):
        for i in range(20):
            self.pano_pub.publish(String("True"))


    def getSonar_f(self, data):
        self.distance_f = data.range

    def getSonar_b(self, data):
        self.distance_b = data.range


    def getImage(self, data):
        #Convert image to OpenCV format
        try:
            cv_image = self.bridge.compressed_imgmsg_to_cv2(data, 'bgr8')
        except CvBridge as e:
            print(e)

        self.image = cv_image

    def displayImage(self):
        return self.image


    def getVelocity(self, data):
        """
        Updates the velocity vector as self.current_velocity and self.current_angle
        """
        self.current_velocity = data.linear.x
        self.current_angle = data.angular.z
        # rospy.loginfo("current velocity: %f", self.current_velocity)
        # rospy.loginfo("current angle : %f", self.current_angle)
        # rospy.loginfo("current time: %f", self.time.secs)

    def getBattery(self, data):
        """
        Updates battery voltage (Volts)
        """
        self.current_voltage = data.voltage
       
        #rospy.loginfo("battery: %f", self.current_voltage)
 

    def pause_robot(self):
        """
        Stores the old velocity for unpausing before publishing a velocity of zero
        """
        self.old_velocity = (self.current_velocity, self.current_angle)
        self.cmd_vel.publish(Twist())

    def unpause_robot(self):
        """Unpauses the robot and has it restore the velocity before being paused"""
        if self.old_velocity is not None:
            move_cmd = Twist()
            move_cmd.linear.x = self.old_velocity[0]
            move_cmd.angular.z = self.old_velocity[1]
            self.cmd_vel.publish(move_cmd)
            self.old_velocity = None
        else:
            rospy.loginfo("Robot was never paused! Continuing mission")

    def return_to_base(self):
        pass
        #implement the go home protocal that Kathryn was working on

    def visit(self, location):
        pass
        #turn string representation to some location on the map

    def shutdown(self):
        self.pause_robot()

    def rotate(self, angle):
        r = rospy.Rate(10);
        move_cmd = Twist()
        move_cmd.linear.x = 0
        move_cmd.angular.z = -0.1

        for x in range(0,int(math.ceil(float(angle)/(0.2*math.pi)))):
            self.cmd_vel.publish(move_cmd)
            r.sleep()

        self.cmd_vel.publish(Twist())

    def forward(self, vel):
        r = rospy.Rate(10);
        move_cmd = Twist()
        move_cmd.linear.x = 0.1
        move_cmd.angular.z = 0

        for x in range(int(100*float(vel))):
            self.cmd_vel.publish(move_cmd)
            r.sleep()

        self.cmd_vel.publish(Twist())

    def rotate_default(self):
        r = rospy.Rate(10);
        move_cmd = Twist()
        move_cmd.linear.x = 0
        move_cmd.angular.z = -0.1

        for x in range(0,int(math.ceil(360/(0.2*math.pi)))):
            self.cmd_vel.publish(move_cmd)
            r.sleep()

        self.cmd_vel.publish(Twist())

    def forward_default(self):
        r = rospy.Rate(10);
        move_cmd = Twist()
        move_cmd.linear.x = 0.1
        move_cmd.angular.z = 0

        for x in range(100):
            self.cmd_vel.publish(move_cmd)
            r.sleep()

        self.cmd_vel.publish(Twist())


if __name__ == "__main__":
    robo = RoboInfo()
    rospy.loginfo("Starting slack node")
    rospy.spin()