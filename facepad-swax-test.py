# Copyright 2018
# 
# Yaojie Liu, Amin Jourabloo, Xiaoming Liu, Michigan State University
# 
# All Rights Reserved.
# 
# This research is based upon work supported by the Office of the Director of 
# National Intelligence (ODNI), Intelligence Advanced Research Projects Activity
# (IARPA), via IARPA R&D Contract No. 2017-17020200004. The views and 
# conclusions contained herein are those of the authors and should not be 
# interpreted as necessarily representing the official policies or endorsements,
# either expressed or implied, of the ODNI, IARPA, or the U.S. Government. The 
# U.S. Government is authorized to reproduce and distribute reprints for 
# Governmental purposes not withstanding any copyright annotation thereon. 
# ==============================================================================
#
# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
''' Tutorial code to use facePAD model
This tutorial can test the face anti-spoofing system on both video and image 
files. 

Examples:
	python facepad-test.py -input ./examples/ex1.mov -isVideo 1 
	python facepad-test.py -input ./examples/ex1.jpg -isVideo 0

Model Input: 
	image: Cropped face in RGB. Ideal size should be larger than 256*256
	
Model Output:
	score: liveness score, range [-1,1]. Higher score (--> 1) denotes spoofness.
	
Other usage:
	Pretrained model can also deploy via Tensorflow Serving. The instruction of 
Tensorflow Serving can be found at:

https://www.tensorflow.org/serving/serving_basic

The signature of the model is:

	inputs  = {'images': facepad_inputs}
	outputs = {'depths': facepad_output_depth,
			   'scores': facepad_output_scores}
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
import cv2
import sys
import os
import time

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# face detector && pad set-up
faced_dir = './haarcascade_frontalface_alt.xml'
export_dir = './lib'
faceCascade = cv2.CascadeClassifier(faced_dir)

# Basic model parameters.
IMAGE_SIZE = 256 #input image size

# name_scope
inputname = "input:0"
outputname = "Mean_2:0"#SecondAmin/

def facePAD_API(image):
	'''
	API Input: 
		image: Cropped face in RGB at any size. Ideally, image is larger than 
		256*256 and the dtype is uint8

	API Output:
		score: liveness score, float32, range [-1,1]. Higher score (--> 1) 
		denotes spoofness.
	'''
	with tf.Session() as sess:
		# load the facepad model
		tf.saved_model.loader.load(sess, 
					[tf.saved_model.tag_constants.SERVING], 
					export_dir)
		_input = tf.get_default_graph().get_tensor_by_name(inputname)
		_output = tf.get_default_graph().get_tensor_by_name(outputname)
		score = sess.run(_output,feed_dict={_input : image})
	return score

def evaluate_image_bbox(imfile,scfile):
	with tf.Session() as sess:
		# load the facepad model
		tf.saved_model.loader.load(sess, 
					[tf.saved_model.tag_constants.SERVING], 
					export_dir)
		image  = tf.get_default_graph().get_tensor_by_name(inputname)
		scores = tf.get_default_graph().get_tensor_by_name(outputname)
		
		# get the image
		frame = cv2.imread(imfile)
		# detect faces in the frame. Detected face in faces with (x,y,w,h)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		faces = faceCascade.detectMultiScale(
			gray,
			scaleFactor=1.1,
			minNeighbors=5,
			minSize=(256,256)
			)
		try:
			faces = sorted(faces, key=lambda x:x[2]) 
			faces = [faces[0]] # only process the largest face
		except:
			print("No face detected!")
			#sys.exit()
		for (x, y, w, h) in faces:
			# crop face from frame
			l = max(w,h)
			face_raw = frame[y:y+l, x:x+l]
			# run the facepad
			sc = sess.run(scores,feed_dict={image : frame})
			# save the score for video frames
			scfile.write("%.3f\n" % sc)
	return scfile

def evaluate_video_bbox(vdfile,scfile):
	# get the video
	video_capture = cv2.VideoCapture(vdfile)
	bbox = np.loadtxt(vdfile[:-3]+'txt',dtype=np.str,delimiter=',')
	bbox = bbox[:,1:]
	(major_ver, _, _, _) = (cv2.__version__).split('.')
	if int(major_ver) < 3:
		totalframes = video_capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)
	else:
		totalframes = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
		
	with tf.Session() as sess:
		# load the facepad model
		tf.saved_model.loader.load(sess, 
					[tf.saved_model.tag_constants.SERVING], 
					export_dir)
		image  = tf.get_default_graph().get_tensor_by_name(inputname)
		scores = tf.get_default_graph().get_tensor_by_name(outputname)

		# container for last frame's detected faces
		last_time_face = []
		fr = 0
		while(fr < totalframes and fr < bbox.shape[0]):
			# get the frame from video
			_, frame = video_capture.read()
			x = int(bbox[fr,0])
			y = int(bbox[fr,1])
			w = int(bbox[fr,2]) - int(bbox[fr,0])
			h = int(bbox[fr,3]) - int(bbox[fr,1])
			fr += 1
			
			l = max(w,h)
			dl = l * 1.5 / 2
			x = int(x - dl)
			y = int(y - 1.1*dl)
			l = int(l + dl + dl)
			# crop face from frame
			face_raw = frame[y:y+l, x:x+l]
			#cv2.imshow('image',face_raw)
			#cv2.waitKey(0)
			#input()
			# run the facepad
			start = time.time()
			sc = sess.run(scores,feed_dict={image : face_raw})
			# save the score for video frames
			scfile.write("%.3f\n" % sc)
			print(sc)
	return scfile

def evaluate_video(vdfile,scfile):
	# get the video
	video_capture = cv2.VideoCapture(vdfile)
	print(video_capture)
	totalframes = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
		
	with tf.compat.v1.Session() as sess:
		# load the facepad model
		tf.saved_model.loader.load(sess, 
					[tf.saved_model.tag_constants.SERVING], export_dir)
		image  = tf.compat.v1.get_default_graph().get_tensor_by_name(inputname)
		scores = tf.compat.v1.get_default_graph().get_tensor_by_name(outputname)

		# container for last frame's detected faces
		last_time_face = []
		ret = True
		while(ret):
			# get the frame from video
			ret, frame = video_capture.read()
			if ret:
				# process image
				sc = sess.run(scores,feed_dict={image : frame})
				# show images
				cv2.imshow('teste', frame)
				cv2.waitKey(10)
				# save the score for video frames
				scfile.write("%.3f\n" % sc)
				print(sc)
	return scfile


def evaluate_image(imfile, scfile, label):
	with tf.Session() as sess:
		# load the facepad model
		tf.saved_model.loader.load(sess, 
					[tf.saved_model.tag_constants.SERVING], 
					export_dir)
		image  = tf.get_default_graph().get_tensor_by_name(inputname)
		scores = tf.get_default_graph().get_tensor_by_name(outputname)
		
		# get the image
		frame = cv2.imread(imfile)
		try:
			# run the facepad
			sc = sess.run(scores,feed_dict={image : frame})
			# save the score for video frames
			#scfile.write("%.3f\n" % sc)
			scfile.write("{} {} \n".format(label, sc))
		except:
			print("Empty image file!")
			#sys.exit()
	return scfile

def getopts(argv,opts):
	while argv:  # While there are arguments left to parse...
		if argv[0][0] == '-':  # Found a "-name value" pair.
			if argv[0][1] == 'h':
				print('-h : help')
				print('-input : STRING, the path to the testing video')
				print('-isVideo : True/False, indicate if it is a video. Default as False.')
			sys.exit()
			opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
		argv = argv[1:]  # Reduce the argument list by copying it starting from outer 1.
	return opts

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.metrics import precision_recall_curve, auc
from myPlots import MyPlots

with tf.Session() as sess:
	# load the facepad model
	tf.saved_model.loader.load(sess, 
				[tf.saved_model.tag_constants.SERVING], 
				export_dir)
	image  = tf.get_default_graph().get_tensor_by_name(inputname)
	scores = tf.get_default_graph().get_tensor_by_name(outputname)

	valid_file_name = './SWAX_Dataset/Protocol-04-valid.json'
	test_file_name = './SWAX_Dataset/Protocol-04-test.json'

	sc_valid_file = open('./score/swax_valid.score','w')
	sc_probe_file  = open('./score/swax_probe.score','w')

	sc_valid_file.write(valid_file_name + '\n')
	sc_probe_file.write( test_file_name + '\n')

	threshold_list = list()
	with open(valid_file_name) as infile:
		protocol_file = json.load(infile)
		for (outer, fold) in enumerate(protocol_file):
			print('>> FOLD {}'.format(outer))
			sc_valid_file.write('>> FOLD {}\n'.format(outer))
			validation_labels = list()
			validation_scores = list()
			for inner, (img_path, img_label) in enumerate(fold):
				# Evaluate validation image
				img_name = os.path.join('SWAX_Dataset', img_path)
				img_file = cv2.imread(img_name, cv2.IMREAD_COLOR)
				img_scre = sess.run(scores, feed_dict={image : img_file})
				# Keep validation results record
				validation_labels.append(-1) if img_label == 'real' else validation_labels.append(+1)
				validation_scores.append(img_scre)
				# Notify user of prediction progress
				sc_valid_file.write("{} {} {} {}\n".format(inner, img_name, img_label, img_scre))
				print(inner, img_name, img_label, img_scre)
			# Obtain threshold
			precision, recall, threshold = precision_recall_curve(validation_labels, validation_scores)
			fmeasure = [(thr, (2 * (pre * rec) / (pre + rec))) for pre, rec, thr in zip(precision[:-1], recall[:-1], threshold)]
			fmeasure.sort(key=lambda tup:tup[1], reverse=True)
			threshold_list.append(str(fmeasure[0][0]))
			with open('./score/swax_thresh.json','w') as outfile:
				json.dump(threshold_list, outfile) 
			print('-> THRESHOLD {}'.format(fmeasure[0][0]))


	error_list = list()
	labels_list = list()
	scores_list = list()
	with open(test_file_name) as infile:
		protocol_file = json.load(infile)
		for (outer, fold) in enumerate(protocol_file):
			threshold_value = threshold_list[outer]
			print('>> FOLD {} - Threshold = {}'.format(outer, threshold_value))
			sc_probe_file.write('>> FOLD {}\n'.format(outer))
			testing_labels = list()
			testing_scores = list()			
			counter_dict = {img_label:0.0 for (img_path, img_label) in fold}
			mistake_dict = {img_label:0.0 for (img_path, img_label) in fold}
			for inner, (img_path, img_label) in enumerate(fold):
				# Evaluate testing image
				img_name = os.path.join('SWAX_Dataset', img_path)
				img_file = cv2.imread(img_name, cv2.IMREAD_COLOR)
				img_scre = sess.run(scores, feed_dict={image : img_file})
				# Keep testing results record
				testing_labels.append(-1) if img_label == 'real' else testing_labels.append(+1)
				testing_scores.append(img_scre)
				pred_label = 'real' if img_scre <= threshold_value else 'wax'
				if pred_label != img_label: 
					mistake_dict[img_label] += 1
				counter_dict[img_label] += 1
				# Notify user of prediction progress
				sc_probe_file.write("{} {} {} {} {} {} {}\n".format(inner, counter_dict, mistake_dict, img_name, img_scre, img_label, pred_label))
				print(inner, counter_dict, mistake_dict, img_name, img_scre, img_label, pred_label)
			# Keep record of APCER, BPCER and ROC
			error_list.append({label:(mistake_dict[label]/counter_dict[label]) for label in counter_dict.keys()})
			labels_list.append(testing_labels)
			scores_list.append(testing_scores)
			with open('./score/swax_acer.json','w') as outfile:
				json.dump(error_list, outfile) 
			with open('./score/swax_roc.json','w') as outfile:
				json.dump({'labels':[str(label) for label in labels_list], 'scores':[str(score) for score in scores_list]}, outfile) 
			# Generate ROC Curve
			plt.figure()
			roc_data = MyPlots.merge_roc_curves(labels_list, scores_list, name='ROC Average')
			MyPlots.plt_roc_curves([roc_data,])
			plt.savefig('./score/swax_roc.pdf')
			plt.close()
