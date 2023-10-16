import cv2
import mediapipe as mp
from ultralytics import YOLO
import datetime
import os
from django.conf import settings
import datetime
import boto3
import numpy as np

# 전역 변수 선언

# 시간 설정
time = datetime.datetime.now()
str_time = str(time.year) + str(time.month) + str(time.day) + str(time.hour) + str(time.minute)
str_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
# S3 클라이언트 설정
s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
# 모델 선언
model = YOLO('best.pt')

# 함수

# 이미지 S3 업로드
def save_image_to_s3(image, str_time):
    image_name = 'finger/'+ str_time + '_clear.jpg'
    s3r = boto3.resource('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    body_data = image.tostring()
    s3r.Bucket('nomercybucket').put_object(Key=image_name, Body=body_data, ContentType='jpg')
    return image_name


# 이미지 Detect
class DetectImageFinger:
    # 이미지 경로 가져오기
    def __init__(self, image_paths):
        self.IMAGE_FILES = image_paths
        self.mp_hands = mp.solutions.hands
    
    # 이미지 처리
    def process_images(self):
        image = self.load_and_preprocess_image()
        results = self.detect_hand_landmarks(image)

        if not results.multi_hand_landmarks:
            result = "safe"
        else: 
            model_result = self.process_hand_landmarks(results.multi_hand_landmarks[0], image)
            if model_result:
                result = self.save_blurred_image(image)
            else:
                result = "safe"
        return result
    
    # 손 끝 인식
    def process_hand_landmarks(self, hand_landmarks, image):
        landmark_4 = hand_landmarks.landmark[4] 
        landmark_8 = hand_landmarks.landmark[8]
        landmark_12 = hand_landmarks.landmark[12]
        landmark_16 = hand_landmarks.landmark[16]
        landmark_20 = hand_landmarks.landmark[20]
        image_height, image_width, _ = image.shape
        model_result = False

        for i in range(4, 21, 4):
            for landmark in [landmark_4, landmark_8, landmark_12, landmark_16, landmark_20]:
                x_px = hand_landmarks.landmark[i].x * image_width
                y_px = hand_landmarks.landmark[i].y * image_height
                annotated_image = image[int(y_px) - 20:int(y_px) + 20, int(x_px) - 20:int(x_px) + 20]
                detections = self.run_model_on_annotated_image(annotated_image)

                for det in detections:
                    if int(det[5]) == 2:
                        image = self.blur_detected_region(image, x_px, y_px)
                        model_result = True

        return model_result

    # 이미지 파일 불러오기
    def load_and_preprocess_image(self):
        image_data = self.IMAGE_FILES
        image = cv2.flip(cv2.imdecode(np.frombuffer(image_data, np.uint8), -1), 1)
        return image

    # 손 끝 인식 초기화
    def detect_hand_landmarks(self, image):
        with self.mp_hands.Hands(
            static_image_mode=True,
            max_num_hands=2,
            min_detection_confidence=0.5) as hands:
            return hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # 모델 적용
    def run_model_on_annotated_image(self, annotated_image):
        results = model(annotated_image, augment=True)
        tensor_list = results[0].boxes.data
        return tensor_list.tolist()

    # 자른 이미지 blur 처리
    def blur_detected_region(self, image, x_px, y_px):
        annotated_image = cv2.blur(image[int(y_px)-20:int(y_px)+20, int(x_px)-20:int(x_px)+20], (5, 5))
        image[int(y_px)-20:int(y_px)+20, int(x_px)-20:int(x_px)+20] = annotated_image
        return image

    # blur 처리 이미지 적용하기
    def save_blurred_image(self, image):
        cv2.imwrite('media/finger/'+str_time+'_clear.png', cv2.flip(image, 1))
        _, encoded_image = cv2.imencode('.jpg', image)
        return save_image_to_s3(encoded_image, str_time)
        
            
# 동영상 Detect
class DetectVideoFinger:
    # 동영상 경로 가져오기
    def __init__(self, video_path):
        self.VIDEO_FILE = video_path
        self.mp_hands = mp.solutions.hands
    
    # 동영상 처리
    def process_video(self):
        hands = self.initialize_hands()
        cap = cv2.VideoCapture(self.VIDEO_FILE, cv2.CAP_ANY)
        out = self.initialize_video_writer(cap)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = self.process_frame(frame, hands)
            out.write(image)

        out.release()
        cap.release()

        return self.get_video_path()
    
    # 손 끝 인식
    def initialize_hands(self):
        return self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5
        )
    
    # 동영상 경로 설정
    def get_video_path(self):
        return os.path.join('media/finger/', str_time + '_clear.mp4')
    
    # 동영상 읽어와서 저장
    def initialize_video_writer(self, cap):
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        video_path = self.get_video_path()
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        return cv2.VideoWriter(video_path, fourcc, 30, (frame_width, frame_height))

    # 동영상 후처리
    def process_frame(self, frame, hands):
        image = cv2.flip(frame, 1)
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if not results.multi_hand_landmarks:
            final_image = image

        for hand_landmarks in results.multi_hand_landmarks:
            image = self.process_hand_landmarks(image, hand_landmarks)
            final_image = image
        return final_image
    
    # 동영상 후처리(landmark 존재 시 실행할 후처리)
    def process_hand_landmarks(self, image, hand_landmarks):
        landmark_4 = hand_landmarks.landmark[4]
        landmark_8 = hand_landmarks.landmark[8]
        landmark_12 = hand_landmarks.landmark[12]
        landmark_16 = hand_landmarks.landmark[16]
        landmark_20 = hand_landmarks.landmark[20]

        image_height, image_width, _ = image.shape
        
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
        return blur_image