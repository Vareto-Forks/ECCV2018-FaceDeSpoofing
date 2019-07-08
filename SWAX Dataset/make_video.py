import cv2 as cv
import imutils
import os

crop_size = 0.90
duplicate_frame = 10
figures = True
inc_value = 2

if figures:
	subfolder = 'crop_Estatuas'
else:
	subfolder = 'crop_Pessoas'

dataset_dict = dict()
for root, dirs, files in os.walk(subfolder):
	for name in files:
		if name.endswith('.jpg'):
			if root in dataset_dict:
				dataset_dict[root].append(name)
			else:
				dataset_dict[root] = [name]


def make_video(image_file, image_name):
	new_name = image_name.replace('.jpg', '.avi')
	image_height, image_width, image_channel = image_file.shape
	crop_height, crop_width = int(image_height * crop_size), int(image_width * crop_size)

	probe_fourcc = cv.VideoWriter_fourcc(*'MP42')
	videoW = cv.VideoWriter(new_name, probe_fourcc, 30.0, (crop_width, crop_height))

	axisYbeg, axisXbeg = 0,0
	axisYend, axisXend = image_height - crop_height, image_width - crop_width

	pos_inc = True
	angle_idx = 0
	angle_lst = [0, -1, -2, -3, -2, -1, 0, +1, +2, +3, +2, +1]
	while (axisYbeg < axisYend - 1) or (axisXbeg < axisXend - 1):
		image_rota = imutils.rotate(image_file, angle_lst[angle_idx % len(angle_lst)])
		image_crop = image_rota[axisYbeg:axisYbeg+crop_height, axisXbeg:axisXbeg+crop_width]
		angle_idx += 1
		
		if pos_inc:
			axisXbeg += inc_value
		else:
			axisXbeg -= inc_value
		if (axisXbeg >= axisXend) or (axisXbeg <= 0):
			axisYbeg += inc_value * 2
			pos_inc = not pos_inc

		videoW.write(image_crop)
		# cv.imshow('teste', image_crop)
		# cv.waitKey(0)
	videoW.release()


for subject_name in dataset_dict.keys():
	for sample_name in dataset_dict[subject_name]:
		full_name = os.path.join(subject_name, sample_name)
		print(full_name)
		image_file = cv.imread(full_name)
		orig_file = cv.resize(image_file, (250,250), interpolation=cv.INTER_AREA)
		flip_file = cv.flip(orig_file, 1)
		make_video(orig_file, full_name.replace('.jpg', '_o.jpg'))
		make_video(flip_file, full_name.replace('.jpg', '_f.jpg'))

