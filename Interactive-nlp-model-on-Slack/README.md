# Interactive-nlp-model-on-Slack
● clean.py
  This file is responsible for cleaning the sentence that user enters before running model.py. Cleaning process includes removing punctuation, tokenization, misspelling correction, stopwords filtering, lemmatisation, stemming and removing repetitive words.

● load.py
  This file is responsible for loading dictionary used for the nlp model.

● my_dict_train.npy
  This file is the dictionary that trained and used by the nlp model.

● model.py
  This file is responsible for key functions of the nlp model.

● slack_bot_init.py
  This file is the only one needs to be run in terminal. It will start the slack node, receive strings from slack channel, then run clean.py and model.py to classify the input into one or multiple groups.

● slack_bot_commands.py
  This file is responsible for relating each group with its corresponding action function in robot_msgs.py.

● robot_msgs.py
  This file is responsible for subscribing and publishing nodes of different from ROS.
