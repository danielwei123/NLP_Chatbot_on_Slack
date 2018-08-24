import numpy as np

read_dictionary = np.load('my_dict_train.npy').item()

for i in read_dictionary.keys():
	print(i,':', read_dictionary[i]) 
	
# read_dictionary['speed'] = set(['speed', 'quick', 'fast', 'veloc'])
# np.save('my_dict_train.npy', read_dictionary)