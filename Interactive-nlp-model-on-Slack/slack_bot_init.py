from __future__ import unicode_literals
from slackclient import SlackClient
from keras.models import load_model
from slack_commands import slack_bot_commands
from slack_commands import robot_msgs
import re
import clean
import model
import cv2
import keras

global check_status, temp_word, temp_label, possible_list, possible_labels

MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def classify(commandString):
    global check_status, temp_word, temp_label, possible_list, possible_labels

    command = clean.clean_word(commandString)

    check_status, temp_label, temp_word, possible_list, possible_labels = model.check_status_func(command)

    key_info = ''

    pano_set = clean.clean_word("panoramic, panorama, pano")

    if pano_set & command == set():
        if check_status == 'Uncertain':
            check_status, temp_label, temp_word, possible_list, possible_labels = model.uncertain(slack_client, channel, starterbot_id)

        if check_status == 'Correct':
            model.correct(slack_client, channel)

        else:
            check_status, temp_label, temp_word, possible_list, possible_labels = model.wrong(command, slack_client, channel, starterbot_id)

    else:
        temp_label = 'panoramic'

    if temp_label == 'attention':
        obj_list = clean.clean_word('chair, outlet, marker')
        for i in obj_list:
            if i in command:
                key_info = i
                break

    if temp_label in ['rotate', 'forward']:
        # extract numerical values
        commandString=clean.remove_bot_num(commandString)
        coordinatePoints= re.findall(r"[+-]?\d+(?:\.\d+)?", commandString)  # coordinatePoints is a list

        if len(coordinatePoints) > 0:
            key_info = coordinatePoints[0]
        # else:
            # key_info = coordinatePoints
        print(key_info)
        
    if temp_label == 'location':

        commandString=clean.remove_bot_num(commandString)
        coordinatePoints= re.findall(r"[+-]?\d+(?:\.\d+)?", commandString)
        if len(coordinatePoints) > 1:
            key_info = coordinatePoints[:2]
        else:
            key_info = clean.search_location(commandString)


    return temp_label, key_info


if __name__ == '__main__':
    slack_client = SlackClient("xoxb-151134378128-381943266085-Rq687iYzMdRVNK98SQThzwQ9")

    # robo = robot_msgs.RoboInfo()
    robo1 = robot_msgs.RoboInfo('1')
    robo2 = robot_msgs.RoboInfo('2')
    robo3 = robot_msgs.RoboInfo('3')
    robo4 = robot_msgs.RoboInfo('4')

    if slack_client.rtm_connect(with_team_state=False):
        model_chairs = load_model('/home/beyondlimits/projects/ClaptrapSystem/web_interface/app/SlackStuff/slack_commands/network_weights/chairs_best_weights.h5',
            custom_objects={'relu6': keras.applications.mobilenetv2.mobilenet_v2.relu6})
        model_outlets = load_model('/home/beyondlimits/projects/ClaptrapSystem/web_interface/app/SlackStuff/slack_commands/network_weights/outlets_best_weights.h5',
            custom_objects={'relu6': keras.applications.mobilenetv2.mobilenet_v2.relu6})
        model_markers = load_model('/home/beyondlimits/projects/ClaptrapSystem/web_interface/app/SlackStuff/slack_commands/network_weights/markers_best_weights.h5',
            custom_objects={'relu6': keras.applications.mobilenetv2.mobilenet_v2.relu6})

        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]

        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            # print(slack_client.rtm_read())

            check_status, temp_word, temp_label, key_info, possible_list, possible_labels = '', '', '', '', [], set()
    
            if command: #if command exists
                print("You sent the command [", command, "] in channel [", channel, "]")

                index_list = clean.get_bot_num(command)

                #check if user specify which robot to use
                if len(index_list) == 0:
                    slack_client.api_call("chat.postMessage",
                            channel = channel,
                            text = 'Sorry, please specify which robot you wanna use?')
                    continue

                task_list = clean.splitSentence(command)    # split command paragraph into seperate sentences
                
                for index in index_list:

                    for task in task_list:

                        label, key_info = classify(task)

                        response = 'label:' + label + ' key_info:' + str(key_info) + ' bot:' + index

                        slack_client.api_call("chat.postMessage",
                            channel = channel,
                            text = response)
                        
                        # slack_bot_commands2.handle_command(response, channel, slack_client, robo, model_chairs, model_outlets, model_markers)

                        if index == '1':
                            slack_bot_commands2.handle_command(response, channel, slack_client, robo1, model_chairs, model_outlets, model_markers)
                        if index == '2':
                            slack_bot_commands2.handle_command(response, channel, slack_client, robo2, model_chairs, model_outlets, model_markers)
                        if index == '3':
                            slack_bot_commands2.handle_command(response, channel, slack_client, robo3, model_chairs, model_outlets, model_markers)
                        if index == '4':
                            slack_bot_commands2.handle_command(response, channel, slack_client, robo4, model_chairs, model_outlets, model_markers)
