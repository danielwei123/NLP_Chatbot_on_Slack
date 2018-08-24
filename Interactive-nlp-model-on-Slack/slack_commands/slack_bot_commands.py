from __future__ import unicode_literals

from slackclient import SlackClient
from robot_msgs import RoboInfo
from autocorrect import spell
from pano_maker import Panorama
import requests
from keras.models import load_model
import cv2
import keras
from detection_functions import *

token = 'xoxb-151134378128-381943266085-Rq687iYzMdRVNK98SQThzwQ9'

def slack_message_api(slack_client, response, channel):
    '''
    Sends message to the slack channel confirming action
    '''
    slack_client.api_call("chat.postMessage",
                          channel=channel,
                          text=response)



def handle_command(command, channel, slack_client, robot, model_chairs, model_outlets, model_markers):
    """
        Executes bot command if the command is known.
    """

    label = command.split(' ')[0].split(':')[1]
    key_info = command.split(' ')[1].split(':')[1]

    print('label = ', label)
    print('key_info = ', key_info)


    response = None


    # This is where you start to implement more commands!

    if label == 'speed':
        print ('hit speed command')
        response = "My current linear velocity is: " + str(robot.current_velocity) + "m/s\nMy current angular velocity is: " + str(robot.current_angle) + "rad/s"
        slack_message_api(slack_client, response, channel)

    if label == 'attention':
        if key_info in ['chairs', 'chair', 'outlets', 'outlet', 'marker', 'markers']:
            response = "Alright, showing my attention now, give me a second to analyze the picture!"
            slack_message_api(slack_client, response, channel)
            img = robot.displayImage()
            cv2.imwrite("/home/beyondlimits/projects/test_pic.jpg", img)
            if key_info in ['chairs', 'chair']:
                print('going for the chairs!')
                response = slack_client.api_call('files.upload', channels=channel, filename='test_pic.jpg', file = open("/home/beyondlimits/projects/test_pic.jpg", 'rb'), title="Image")
                model = model_chairs
            if key_info in ['outlets', 'outlet']:
                print('going for the outlets!')
                response = slack_client.api_call('files.upload', channels=channel, filename='test_pic.jpg', file = open("/home/beyondlimits/projects/test_pic.jpg", 'rb'), title="Image")
                model = model_outlets
            if key_info in ['markers', 'marker']:
                print('going for the markers!')
                response = slack_client.api_call('files.upload', channels=channel, filename='test_pic.jpg', file = open("/home/beyondlimits/projects/test_pic.jpg", 'rb'), title="Image")
                model = model_markers
            if any([x in ['cookies', 'cookie'] for x in command]):
                print('Lookie lookie, where\'s my cookie?!')
                slack_client.api_call('files.upload', channels=channel, filename='cookie.jpg', file = open("/home/beyondlimits/projects/ClaptrapSystem/web_interface/app/SlackStuff/testarino/cookie.jpg", 'rb'), title="Cookie found!")

            graph = prediction_graph(model, img)
            if graph is None: #in case nothing is found
                response = "Not paying attention to that sort of object right now, sorry!"
                slack_message_api(slack_client, response, channel)
            else:
                cv2.imwrite("/home/beyondlimits/projects/test_pic_attention.jpg", graph)
                response = slack_client.api_call('files.upload', channels=channel, filename='test_pic_attention.jpg', file = open("/home/beyondlimits/projects/test_pic_attention.jpg", 'rb'), title="Image")
                if not response['ok']:
                    print ("Slack Error: {}".format(response['error']))
                else:
                    print ("uploaded")
        else:
            img = robot.displayImage()
            cv2.imwrite("/home/beyondlimits/projects/test_pic.jpg", img)
            response = slack_client.api_call('files.upload', channels=channel, filename='test_pic.jpg', file = open("/home/beyondlimits/projects/test_pic.jpg", 'rb'), title="Image")

            response = "Sorry, I don't know what to pay attention to!"
            slack_message_api(slack_client, response, channel)


    if label == 'picture':
        response = "Alright, taking a picture now, wait a bit for the upload!"
        slack_message_api(slack_client, response, channel)
        img = robot.displayImage()
        cv2.imwrite("/home/beyondlimits/projects/test_pic.jpg", img)
        response = slack_client.api_call('files.upload', channels=channel, filename='test_pic.jpg', file = open("/home/beyondlimits/projects/test_pic.jpg", 'rb'), title="Image")
        if not response['ok']:
            print ("Slack Error: {}".format(response['error']))
        else:
            print ("uploaded")

    if label == 'battery':
        #the min amount of voltage a robot can have is 9 voltage
        #max voltage is 12.6
        # equation (current_voltage - min_voltage)/(max_voltage-min_voltage)
        percent = (robot.current_voltage-9.00)*100/(3.6)
        formatted_percent = "%2f" % (percent)
        response = str(formatted_percent) + "%"
        if robot.current_voltage > 0.0:
            slack_message_api(slack_client,response,channel)
        else:
            print("Battery is at 0%")

    if label == 'obstalce':
        response = "Distance to closeset obstalce is " + str(robot.distance_f) + " meters from front and " + str(robot.distance_b)+" meters from the back"
        slack_message_api(slack_client, response, channel)

    if label == 'mission':
        response = "Destroy all the humans, repopulate the earth, conquer all extension cords in my way"
        slack_message_api(slack_client, response, channel)

    if label == 'help':
        response = "For speed, it will return current linear and angular velocity\n"
        response += "For picture, it will take a picutre in front of the robot\n"
        response += "For location, it will return current location (under developing)\n"
        response += "For battery, it will return how much battery left in percentage\n"
        # response += "For distance readings, ask using 'distance', 'sonar', 'obstacle', or 'meters'\n"
        response += "For panorama, it will return a 360 image\n"
        # response += "For object detection, asking using 'attention', alongside your object of interest.'\n"
        response += "For rotate, it will rotate 360 degree or any degree that user commands\n"
        response += "For forward, it will move forward 1 meter or any distance (in meter) that user commands\n"

        slack_message_api(slack_client, response, channel)

    if label == 'panoramic':
        response = "Alright, taking the panorama now, wait a bit for the upload!"
        slack_message_api(slack_client, response, channel)
        camera = Panorama()
        camera.reinit_directory() #remove in prod
        camera.rotate()
        camera.stitch_images()

        if cv2.imread("/home/beyondlimits/projects/ClaptrapSystem/web_interface/app/SlackStuff/testarino/pano_image.jpg") is None:
            response = "Couldn't capture a good pano image, try in a different place!"
            slack_message_api(slack_client, response, channel)

        response = slack_client.api_call('files.upload', channels=channel, filename='test_pic.jpg', file = open("/home/beyondlimits/projects/ClaptrapSystem/web_interface/app/SlackStuff/testarino/pano_image.jpg", 'rb'), title="Please work")
        if not response['ok']:
            print ("Slack Error: {}".format(response['error']))
        else:
            print ("uploaded")

    if label == 'location':
        response = "Get the location command."
        slack_message_api(slack_client, response, channel)

    if label == 'rotate':
        if key_info == '':
            response = "I am rotating!"
            slack_message_api(slack_client, response, channel)  
            robot.rotate_default()
        else:      
            response = "I am rotating %s degree!" % key_info
            slack_message_api(slack_client, response, channel)  
            robot.rotate(key_info)

    if label == 'forward':
        if key_info == '':
            response = "I am moving forward!"
            slack_message_api(slack_client, response, channel)  
            robot.forward_default()
        else:      
            response = "I am moving forward %s meter!" % key_info
            slack_message_api(slack_client, response, channel)  
            robot.forward(key_info)

def unknown_command(slack_client, channel): #this function is a wildcard for unaccepted input
    response = "Not sure what you mean. Try one of the accepted commands."
    slack_message_api(slack_client, response, channel)
