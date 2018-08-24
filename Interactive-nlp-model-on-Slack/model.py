from __future__ import unicode_literals
from vocabulary.vocabulary import Vocabulary as vb
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet as wn
from itertools import product
from slackclient import SlackClient
import json
import clean
import spacy
import numpy as np
import re

MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

ps = PorterStemmer()
nlp = spacy.load('en_core_web_md')

# func_list = {'speed':clean.clean_word('speed, velocity'),
# 			 'location':clean.clean_word('location, where'),
# 			 'battery':clean.clean_word('battery, voltage'),
# 			 'picture':clean.clean_word('picture, photo'),
# 			 'panoramic':clean.clean_word('panoramic, panorama'),
# 			 'forward':clean.clean_word('forward, ahead'),
# 			 'rotate':clean.clean_word('rotate'),
# 			 'attention':clean.clean_word('attention'),
# 			 'help':clean.clean_word('help')}

func_list = read_dictionary = np.load('my_dict_train.npy').item()

num_list = {1:'speed', 
			2:'location', 
			3:'battery',
			4:'picture',
			5:'panoramic',
			6:'forward',
			7:'rotate',
			8:'attention',
			9:'help'}

global check_status, temp_word, temp_label, possible_list, possible_labels

def parse_bot_commands(slack_events, starterbot_id):
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

def recheck(text, slack_client, channel, starterbot_id):

    slack_client.api_call("chat.postMessage",
        channel = channel,
        text = text)
    confirmation = None
    while confirmation is None:
        confirmation, channel = parse_bot_commands(slack_client.rtm_read(), starterbot_id)
    
    return confirmation

def takeThird(elem):

	return elem[2]

def check_status_func(sentence):

	global check_status, temp_label, temp_word, possible_list, possible_labels

	check_status = ''
	temp_word = ''
	temp_label = ''
	possible_list = []
	possible_labels = set()

	# if the word is in the func_list
	for word in sentence:
		for lable in func_list.keys():
			for j in func_list[lable]:

				if j == word:
					possible_list.append((word,lable,abs(nlp(word).similarity(nlp(ps.stem(lable))))))
					possible_labels.add(lable)

	possible_list = sorted(possible_list, key=takeThird, reverse=True)

	if len(possible_list) > 0:
		# print(possible_list)

		if len(possible_list) == 1:
			check_status = 'Correct'
		else:
			# check if there is only one lable or similarity is >= 0.8
			if len(possible_labels) == 1 or possible_list[0][2] >= 0.8:
				check_status = 'Correct'
			else:
				check_status = 'Uncertain'

		temp_word = possible_list[0][0]
		temp_label = possible_list[0][1]
	else:
		check_status = 'Wrong'

	return check_status, temp_label, temp_word, possible_list, possible_labels

# if the robot is certain about the answer
def correct(slack_client, channel):
	global check_status, temp_label, temp_word, possible_list, possible_labels
	np.save('my_dict_train.npy', func_list)
	text = 'Your command is "%s".' % temp_label

# if the robot is uncertain about the answer
def uncertain(slack_client, channel, starterbot_id):
	global check_status, temp_label, temp_word, possible_list, possible_labels
	print(possible_list)

	for i in range(len(possible_list)):
		temp_word = possible_list[i][0]
		temp_label = possible_list[i][1]
		text = 'I guess you are talking about the category of "%s" with keyword "%s". Yes or no?' %(temp_label, temp_word)
		
		# ask the user to check if robot gives the correct answer
		user_check = recheck(text, slack_client, channel, starterbot_id)

		if user_check in ['Yes', 'yes', 'Y', 'y']:
			print('Thank you!')
			np.save('my_dict_train.npy', func_list)
			check_status = 'Correct'
			break
		else:
			continue

	if check_status != 'Correct':
		check_status = 'Wrong'

	# return check_status
	return check_status, temp_label, temp_word, possible_list, possible_labels

# if no match or wrong answer
def wrong(sentence, slack_client, channel, starterbot_id):

	global check_status, temp_label, temp_word, possible_list, possible_labels

	text = 'I\'m not sure. Please teach me which category does this sentence fall into:\n1. speed\n2. location\n3. battery\n4. picture\n5. panoramic\n6. forward\n7. rotate\n8. attention\n9. help\n10. None of the above\nPlease enter 1-10: '
	
	while True:
		try:
			index = int(recheck(text, slack_client, channel, starterbot_id))
			break
		except ValueError:
			slack_client.api_call("chat.postMessage",
                channel = channel,
                text = 'That was no valid number. Try again...')

	if index in [1,2,3,4,5,6,7,8,9]:
		# find the word with the greatest similarity with the lable word
		# double check with user, and then add the word into dict if the user says 'yes'

		index = int(index)
		temp_label = num_list[index]
		sentence = sorted(sentence, key=lambda w: nlp(num_list[index]).similarity(nlp(w)), reverse=True)

		guess_time = 0	# how many times the robot guess which word in the sentence matches the label

		for word in sentence[:3]:

			# print('I guess the word "%s" belongs to the category of "%s". Yes or no?' %(word,num_list[index]))
			text = 'I guess the word "%s" belongs to the category of "%s". Yes or no?\ntype Yes or No: ' %(word,num_list[index])		
			user_check = recheck(text, slack_client, channel, starterbot_id)

			if user_check in ['Yes', 'yes', 'Y', 'y']:
				# print('Thank you!')
				slack_client.api_call("chat.postMessage",
					channel = channel,
					text = 'Thank you!')
				func_list[num_list[index]].add(word)
				np.save('my_dict_train.npy', func_list)
				break

			else:
				# print('Sorry, I made a mistake.')
				slack_client.api_call("chat.postMessage",
					channel = channel,
					text = 'Sorry, I made a mistake.')
				guess_time += 1

		if guess_time == 3:
			# print('Sorry, I can\'t classify this sentence. Please try another one.')
			text = 'Sorry, I can\'t classify this sentence. Please try another one.'
			slack_client.api_call("chat.postMessage",
					channel = channel,
					text = text)
	else:
			# print("Your command is not correct.")
			text = "Your command does not belong to existing groups.\nPlease enter another sentence:"
			slack_client.api_call("chat.postMessage",
				channel = channel,
				text = text)

	return check_status, temp_label, temp_word, possible_list, possible_labels
