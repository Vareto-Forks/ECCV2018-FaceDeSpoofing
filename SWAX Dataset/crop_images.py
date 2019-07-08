from mtcnn.mtcnn import MTCNN
import cv2 as cv 
import os

detector = MTCNN()
subfolder = 'Estatuas'
outfolder = 'crop_' + subfolder

sample_counter = 0
dataset_dict = dict()
for root, dirs, files in os.walk(subfolder):
	for name in files:
		if name.endswith('.jpg'):
			if root in dataset_dict:
				dataset_dict[root].append(name)
			else:
				dataset_dict[root] = [name]
			sample_counter += 1

face_counter = 0
for subject_name in dataset_dict.keys():
	for sample_name in dataset_dict[subject_name]:
		new_subject_name =  'crop_' + subject_name
		if not os.path.exists(new_subject_name):
			os.makedirs(new_subject_name)

		print(os.path.join(subject_name, sample_name))
		try:
			sample_file = cv.imread(os.path.join(subject_name, sample_name))
			faces_list = detector.detect_faces(sample_file)
			if len(faces_list) == 1:
				face_bbox = faces_list[0]['box']
				print(face_bbox)
				padding = (int(face_bbox[2] * 0.2), int(face_bbox[3] * 0.2))
				croppd_face = sample_file[face_bbox[1]-padding[1]:face_bbox[1]+face_bbox[3]+padding[1], face_bbox[0]-padding[0]:face_bbox[0]+face_bbox[2]+padding[0]]
				croppd_face = cv.resize(croppd_face, (250,250), interpolation=cv.INTER_AREA)
				face_counter += 1
				# cv.imshow('cropped', croppd_face)
				# cv.waitKey(0)
				cv.imwrite(os.path.join(new_subject_name, sample_name), croppd_face)
		except:
			print('Face image error')

print('IMAGE_LIST', sample_counter)
print('FACE_COUNTER', face_counter)
