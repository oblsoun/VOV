import cv2
import mediapipe as mp
from ultralytics import YOLO
import datetime
import os
from django.conf import settings
from io import BytesIO
import numpy as np
import boto3

model = YOLO('best.pt')

class DetectImageFinger:
    def __init__(self, image_paths):
        self.IMAGE_FILES = image_paths
        self.mp_hands = mp.solutions.hands
        self.str_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    # s3 이미지 저장하는  함수
    def save_image_to_s3(self, image):
        image_name = 'uploads/' + self.str_time + '_clear.jpg'
        s3r = boto3.resource('s3',
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        body_data = image.tostring()
        s3r.Bucket('nomercybucket').put_object(Key=image_name, Body=body_data, ContentType='jpg')
    
    # 파일 이름 가져오는 함수
    def get_file_name(self):
        if hasattr(self, 'file_name'):
            result = self.file_name
        else:
            result = ''
        return result
    
    # 이미지 모델 가져와서 처리하는 과정
    def process_images(self):
        danger_flag = 'danger'

        with self.mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=2,
            min_detection_confidence=0.5) as hands:
            image_data = self.IMAGE_FILES
            image = cv2.flip(cv2.imdecode(np.frombuffer(image_data, np.uint8), -1), 1)
            results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            if not results.multi_hand_landmarks:
                danger_flag = 'safe'
            else:
                hand_landmarks = results.multi_hand_landmarks[0]
                landmark_4 = hand_landmarks.landmark[4] 
                landmark_8 = hand_landmarks.landmark[8]
                landmark_12 = hand_landmarks.landmark[12]
                landmark_16 = hand_landmarks.landmark[16]
                landmark_20 = hand_landmarks.landmark[20]

                image_height, image_width, _ = image.shape
                print("Landmark 4: ", landmark_4)
                print("Landmark 8: ", landmark_8)
                print("Landmark 12: ", landmark_12)
                print("Landmark 16: ", landmark_16)
                print("Landmark 20: ", landmark_20)

                for i in range(4, 21, 4):
                    for landmark in [landmark_4, landmark_8, landmark_12, landmark_16, landmark_20]:
                        x_px = hand_landmarks.landmark[i].x * image_width
                        y_px = hand_landmarks.landmark[i].y * image_height

                        annotated_image = image[(int(y_px) - 20):(int(y_px) + 20), (int(x_px) - 20):(int(x_px) + 20)]
                    results = model(annotated_image, augment=True)
                    tensor_list = results[0].boxes.data
                    detection = tensor_list.tolist()
                    for det in detection:
                        cls = det[5]
                        blur_image = image
                        if int(cls) == 2:
                            annotated_image = cv2.blur(annotated_image, (5, 5))
                            blur_image[(int(y_px)-20):(int(y_px)+20), (int(x_px)-20):(int(x_px)+20)] = annotated_image

                    cv2.imwrite('media/finger/' + self.str_time + '_clear.png', cv2.flip(blur_image, 1))
                    _, encoded_image = cv2.imencode('.jpg', blur_image)
                    self.save_image_to_s3(encoded_image)


                    self.file_name = 'uploads/' + self.str_time + '_clear.jpg'

        return danger_flag
