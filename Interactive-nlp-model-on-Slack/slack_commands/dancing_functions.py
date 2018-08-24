import rospy
from geometry_msgs.msg import Twist


class Robodancer():
    def __init__(self):
        # tell user how to stop TurtleBot
        rospy.loginfo("To stop TurtleBot CTRL + C")
        # call shutdown() on ctrl+c
        rospy.on_shutdown(self.shutdown)
        # Publish Twist to cmd_vel
        self.cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=10)

        rate = rospy.Rate(5);

        # Twist is a datatype for velocity
        move_cmd = Twist()

        # do a dance 5 times
        count = 0
        while count < 6:
            # move forward
            move_cmd.linear.x = 0.2
            # turn at 0 radians/s
            move_cmd.angular.z = 0
            # publish the velocity
            self.cmd_vel.publish(move_cmd)
            rate.sleep()

            move_cmd.linear.x = 0
            self.cmd_vel.publish(move_cmd)
            rate.sleep()

            move_cmd.linear.x = -0.2
            self.cmd_vel.publish(move_cmd)
            rate.sleep()

            move_cmd.linear.x = 0
            self.cmd_vel.publish(move_cmd)
            rate.sleep()

            move_cmd.angular.z = 1.0
            self.cmd_vel.publish(move_cmd)
            rate.sleep()

            move_cmd.angular.z = 0
            self.cmd_vel.publish(move_cmd)
            rate.sleep()

            move_cmd.angular.z = -1.0
            self.cmd_vel.publish(move_cmd)
            rate.sleep()

            move_cmd.angular.z = 1.0
            self.cmd_vel.publish(move_cmd)
            rate.sleep()

            move_cmd.angular.z = 0
            self.cmd_vel.publish(move_cmd)
            rate.sleep()

            move_cmd.angular.z = -1.0
            self.cmd_vel.publish(move_cmd)
            rate.sleep()

            move_cmd.angular.z = 0
            self.cmd_vel.publish(move_cmd)
            rate.sleep()

            move_cmd.linear.x = 0.2
            self.cmd_vel.publish(move_cmd)
            rate.sleep()

            move_cmd.linear.x = 0
            self.cmd_vel.publish(move_cmd)
            rate.sleep()

            move_cmd.linear.x = -0.2
            self.cmd_vel.publish(move_cmd)
            rate.sleep()
            count += 1
            print(count)

        if count == 6:
            self.shutdown()

    def shutdown(self):
        # default Twist is 0 - stops bot
        self.cmd_vel.publish(Twist())
        rospy.loginfo("No dancing!!")
        rospy.sleep(1)
