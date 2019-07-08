import json
import os
import random


extension = '.avi'
folder01 = './crop_real'
folder02 = './crop_wax'
n_folds = 10
split_size = [0.6, 0.2, 0.2]


def randomize_names(file_name='subjects.txt', split_division=[0.6, 0.2, 0.2]):
	cross_dictionary = {'train':[], 'valid':[], 'probe':[]}
	with open('subjects.txt', 'r') as infile:
		subject_list = [line.strip() for line in infile]
		num_items = [round(len(subject_list) * perc) for perc in split_division]
		for index in range(n_folds):
			random.shuffle(subject_list)		
			train_temp = subject_list[:num_items[0]]
			valid_temp = subject_list[num_items[0]:num_items[0]+num_items[1]]
			probe_temp = subject_list[num_items[0]+num_items[1]:]
			cross_dictionary['train'].append(train_temp)
			cross_dictionary['valid'].append(valid_temp)
			cross_dictionary['probe'].append(probe_temp)
	return cross_dictionary


def collect_samples(folder_name, extension, sample_dictionary=None):
	if sample_dictionary == None:
		sample_dictionary = dict()
	for root, dirs, files in os.walk(folder_name):
		for name in files:
			if name.endswith(extension):
				label = 'real' if 'real' in root else 'wax'
				if label in sample_dictionary:
					sample_dictionary[label].append(os.path.join(root, name))
				else:
					sample_dictionary[label] = [os.path.join(root, name)]
	return sample_dictionary


def generate_protocol(protocol_name, subset_list, sample_dictionary):
	split_list = list()
	sample_list = sample_dictionary['real'] + sample_dictionary['wax']
	for split in subset_list:
		pic_list = [sample for subject in split for sample in sample_list if subject in sample]
		tag_list = ['real' if 'real' in item else 'wax' for item in pic_list]
		tup_list = [(pic,tag) for pic,tag in zip(pic_list,tag_list)]
		split_list.append(tup_list)
	with open(protocol_name + '.json', 'w') as outfile:
		json.dump(split_list, outfile)


cross_dict  = randomize_names(file_name='subjects.txt', split_division=[0.8, 0.0, 0.2])
sample_dict = collect_samples(folder01, extension, sample_dictionary=None)
sample_dict = collect_samples(folder02, extension, sample_dictionary=sample_dict)
generate_protocol(protocol_name='Protocol-01-train', subset_list=cross_dict['train'], sample_dictionary=sample_dict)
generate_protocol(protocol_name='Protocol-01-test', subset_list=cross_dict['probe'], sample_dictionary=sample_dict)

cross_dict  = randomize_names(file_name='subjects.txt', split_division=[0.6, 0.2, 0.2])
sample_dict = collect_samples(folder01, extension, sample_dictionary=None)
sample_dict = collect_samples(folder02, extension, sample_dictionary=sample_dict)
generate_protocol(protocol_name='Protocol-02-train', subset_list=cross_dict['train'], sample_dictionary=sample_dict)
generate_protocol(protocol_name='Protocol-02-valid', subset_list=cross_dict['valid'], sample_dictionary=sample_dict)
generate_protocol(protocol_name='Protocol-02-test', subset_list=cross_dict['probe'], sample_dictionary=sample_dict)

cross_dict  = randomize_names(file_name='subjects.txt', split_division=[0.6, 0.2, 0.2])
sample_dict = collect_samples(folder01, extension, sample_dictionary=None)
sample_dict = collect_samples(folder02, extension, sample_dictionary=sample_dict)
generate_protocol(protocol_name='Protocol-03-train', subset_list=cross_dict['train'], sample_dictionary=sample_dict)
generate_protocol(protocol_name='Protocol-03-valid', subset_list=cross_dict['valid'], sample_dictionary=sample_dict)
generate_protocol(protocol_name='Protocol-03-test', subset_list=cross_dict['probe'], sample_dictionary=sample_dict)

cross_dict  = randomize_names(file_name='subjects.txt', split_division=[0.6, 0.2, 0.2])
sample_dict = collect_samples(folder01, extension, sample_dictionary=None)
sample_dict = collect_samples(folder02, extension, sample_dictionary=sample_dict)
generate_protocol(protocol_name='Protocol-04-train', subset_list=cross_dict['train'], sample_dictionary=sample_dict)
generate_protocol(protocol_name='Protocol-04-valid', subset_list=cross_dict['valid'], sample_dictionary=sample_dict)
generate_protocol(protocol_name='Protocol-04-test', subset_list=cross_dict['probe'], sample_dictionary=sample_dict)



# with open('train_split.txt', 'w') as outfile:
# 	for split in cross_dict['train']:
# 		outfile.write(str(len(split)) + '\n')
# 		for item in split:
# 			outfile.write(item + '\n')
# 		outfile.write('\n')


# with open('valid_split.txt', 'w') as outfile:
# 	for split in cross_dict['valid']:
# 		outfile.write(str(len(split)) + '\n')
# 		for item in split:
# 			outfile.write(item + '\n')
# 		outfile.write('\n')

# with open('probe_split.txt', 'w') as outfile:
# 	for split in cross_dict['probe']:
# 		outfile.write(str(len(split)) + '\n')
# 		for item in split:
# 			outfile.write(item + '\n')
# 		outfile.write('\n')