from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, FileResponse
from .models import CapturedImage, MyPhoto, User, Frequency
from .detectApi import DetectImageFinger, DetectVideoFinger
from django.views.decorators.csrf import csrf_exempt
from ultralytics import YOLO
import boto3
from django.core.mail import EmailMessage
import os
import shutil
from os.path import expanduser
from django.conf import settings

REALTIME_TEMPLATES = 'realTimeDeidentificationApp/realTime.html'
aws_storage_bucket_name = settings.AWS_STORAGE_BUCKET_NAME
aws_access_key_id = settings.AWS_ACCESS_KEY_ID
aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
captured_image_path = "captured_images/captured_image.jpg"

def real_time(request):
    user_id = request.session.get('user_id', 'fake')
    context = {'user_id': user_id}
    if user_id != 'fake':
        user = User.objects.get(userid = user_id)
        user_email = user.useremail

        context['user_email'] = user_email

    return render(request, REALTIME_TEMPLATES, context)

# 촬영 이미지 S3에 저장
@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image = request.FILES['image']
            captured_image = CapturedImage(image=image)
            captured_image.save()
            result = redirect('realTimeDeidentificationApp:detect_image')
        except Exception as e:
            result = JsonResponse({'error_message': str(e)})
    return result

# 이미지 후처리
@csrf_exempt
def detect_image(request):
    user_id = request.session.get('user_id', 'fake')

    s3 = boto3.client('s3',
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key)
    input_img = s3.get_object(Bucket=aws_storage_bucket_name, Key=captured_image_path)
    raw_image = input_img['Body'].read()

    detector = DetectImageFinger(raw_image)
    safe_image_key = detector.process_images()

    if safe_image_key == "safe":
        update_frequency_db_safe(user_id)
        result = "안전한 파일입니다"
    else:
        update_myphoto_db(safe_image_key, user_id)
        update_frequency_db_danger(user_id)
        result = "위험한 파일입니다"
    return JsonResponse({'result': result, 'user_id': user_id, 'safe_image_key': safe_image_key})

# Frequency DB 저장
def update_frequency_db_safe(user_id):
    user_instance = User.objects.get(userid=user_id)
    if user_id== "fake":
        user_type = "비회원"
    else:
        user_type = "회원"
    frequency = Frequency(
        userid = user_instance,
        usertype = user_type,
        total = 1,
        safe = 1,
        danger = 0
    )
    frequency.save()
    return user_instance

# Frequency DB 저장
def update_frequency_db_danger(user_id):
    user_instance = User.objects.get(userid=user_id)
    if user_id == "fake":
        user_type = "비회원"
    else:
        user_type = "회원"
    frequency = Frequency(
        userid = user_instance,
        usertype = user_type,
        total = 1,
        safe = 0,
        danger = 1
    )
    frequency.save()
    return user_instance

# Myphoto DB 저장
def update_myphoto_db(safe_image_key, user_id):
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
    image_url = f"https://nomercybucket.s3.amazonaws.com/{safe_image_key}"
    response = s3.head_object(Bucket=aws_storage_bucket_name, Key=safe_image_key)
    object_size_bytes = response['ContentLength']
    object_size_kb = object_size_bytes / 1024
    user_instance = User.objects.get(userid=user_id)
    if user_id != 'fake':
        myphoto = MyPhoto(
            userid=user_instance,
            filename=safe_image_key.split("/")[-1],
            image=image_url,
            filevolume=object_size_kb
        )
        myphoto.save()
    else:
        print(user_instance)
    return response

# 이메일 전송
def send_email(request):
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
    input_img = s3.get_object(Bucket=aws_storage_bucket_name, Key=captured_image_path)
    raw_image = input_img['Body'].read()

    detector = DetectImageFinger(raw_image)
    safe_image_key = detector.process_images()

    detect_image = s3.get_object(Bucket=aws_storage_bucket_name, Key=safe_image_key)
    image_data = detect_image['Body'].read()

    if request.method == 'POST':
            email = request.POST.get('email')
            result = None
            if not email:
                result = JsonResponse({'error': '이메일 주소를 입력해주세요.'}, status=400)
            else:
                try:
                    subject = "[VOV] 파일 전송 메일입니다."
                    message = "안전해진 파일이 첨부파일로 전송되었습니다."
                    from_email = settings.DEFAULT_FROM_EMAIL
                    recipient_list = [email]
                    email_message = EmailMessage(subject, message, from_email, recipient_list)
                        
                    email_message.attach(safe_image_key.split("/")[-1], image_data, 'image/jpeg')  # 이미지 첨부

                    email_message.send(fail_silently=False)

                    result = JsonResponse({'message': '이메일이 성공적으로 전송되었습니다.'})
                except Exception as e:
                    print(f"이메일 전송 오류: {str(e)}")
                    result = JsonResponse({'error': str(e)}, status=500)
    return result

# 다운로드
@csrf_exempt
def download(request):
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
    input_img = s3.get_object(Bucket=aws_storage_bucket_name, Key=captured_image_path)
    raw_image = input_img['Body'].read()

    detector = DetectImageFinger(raw_image)
    safe_image_key = detector.process_images()

    if request.method == 'POST':
        desktop_path = os.path.join(expanduser("~"), 'Desktop')
        local_file_path = os.path.join(desktop_path, safe_image_key.split('/')[-1])
        with open(local_file_path, 'wb') as local_file:
            s3.download_fileobj("nomercybucket", safe_image_key, local_file)
        response = HttpResponse(content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename={safe_image_key.split("/")[-1]}'
        with open(local_file_path, 'rb') as local_file:
            response.write(local_file.read())
    return response

# 비디오 후처리 및 저장
@csrf_exempt
def upload_video(request):
    desktop_path = os.path.expanduser("~/Desktop")
    if request.method == 'POST' and request.FILES.get('video'):
        try:
            video_file = request.FILES['video']
            video_path = 'media/video.mp4'
            with open(video_path, 'wb') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)
            detector = DetectVideoFinger(video_path)
            detector.process_video()
            process_video_path = detector.process_video()
            if os.path.exists(process_video_path):
                try:
                    shutil.copy(process_video_path, desktop_path)
                    result = "안전하게 다운로드 됐습니다."
                except Exception:
                    result = "오류 발생"
        except Exception as e:
            result = "오류 발생"
    return JsonResponse({'result': result})

# 닫기 버튼
@csrf_exempt
def close(request):
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
    if request.method == 'POST':
        s3.delete_object(Bucket=aws_storage_bucket_name, Key=captured_image_path)
    return JsonResponse({'message': '닫기'})
    
