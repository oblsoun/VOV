from django.http import HttpResponse
import os
from posixpath import expanduser
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render
from .detectApi import DetectImageFinger
from .models import Frequency, User, MyPhoto
from .forms import ImageUploadForm 
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import boto3

# 페이지에 접속하는 함수
def file_upload(request):
    total_values = sum(Frequency.objects.values_list('total', flat=True))
    danger_values = sum(Frequency.objects.values_list('danger', flat=True))
    safe_values = sum(Frequency.objects.values_list('safe', flat=True))
    member_values = sum(Frequency.objects.filter(usertype='회원').values_list('total', flat=True))
    nomember_values = sum(Frequency.objects.filter(usertype='비회원').values_list('total', flat=True))
    members = Frequency.objects.filter(usertype="회원")
    result = {}
    for member in members:
        user = member.userid
        if user.userclass1 == '개인':
            userclass2 = user.userclass2
            total = member.total
            if userclass2 in result:
                result[userclass2] += total
            else:
                result[userclass2] = total
    sorted_result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
    top_5 = dict(list(sorted_result.items())[:5])
    context = {'total_values': total_values,
               'danger_values': danger_values,
               'safe_values': safe_values,
               'member_values': member_values,
               'nomember_values': nomember_values,
               'top_5' : top_5}
    
    user_id = request.session.get('user_id', 'fake')
    if user_id != 'fake':
        user = User.objects.get(userid = user_id)
        user_email = user.useremail

        context['user_email'] = user_email

    if 'file_name' not in request.session:
        request.session['file_name'] = 'no_file_name'

    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.save()
            image_filename = image_instance.filename()
            request.session['uploaded_filename'] = image_filename
            detect_image(request)
            file_name = request.session.get('file_name', '')
            context['file_name'] = file_name
    else:
        form = ImageUploadForm()
    
    context['form'] = form
    return render(request, 'fileDeidentificationApp/fileUpload.html', context)

# 이미지를 처리하는 함수
@csrf_exempt
def detect_image(request):
    # S3에서 원본 이미지 가져오기
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    
    uploaded_filename = request.session.get('uploaded_filename', None)
    file_key = f"upload_first/{uploaded_filename}"
    input_img = s3.get_object(Bucket="nomercybucket", Key=file_key)
    raw_image = input_img['Body'].read()

    # DetectImageFinger 클래스를 사용하여 원본이미지 식별 처리
    detector = DetectImageFinger(raw_image)
    detector.process_images()
    danger_flag = detector.process_images()

    request.session['file_name'] = str(detector.get_file_name())
    file_name = request.session.get('file_name', '')
    user_id = request.session.get('user_id', 'fake')

    s3.delete_object(Bucket="nomercybucket", Key=file_key)

    if user_id and danger_flag == 'danger':
        update_myphoto_db(file_name, user_id)
        update_frequency_db_danger(user_id)

    if user_id and danger_flag == 'safe':
        update_frequency_db_safe(user_id)

    return file_name

# myphoto db에 데이터를 주입하는 함수
def update_myphoto_db(safe_image_key, user_id):
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    image_url = f"https://nomercybucket.s3.amazonaws.com/{safe_image_key}"
    response = s3.head_object(Bucket="nomercybucket", Key=safe_image_key)
    object_size_bytes = response['ContentLength']
    object_size_kb = object_size_bytes / 1024
    user_instance = User.objects.get(userid=user_id)
    myphoto = MyPhoto(
        userid=user_instance,
        filename=safe_image_key.split("/")[-1],
        image=image_url,
        filevolume=object_size_kb
    )
    myphoto.save()
    return response

# 안전으로 처리된 경우 frequency db에 데이터를 주입하는 함수
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

# 위험으로 처리된 경우 frequency db에 데이터를 주입하는 함수
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

# 처리된 파일을 이메일로 전송하는 함수
def send_email(request):
    
    safe_image_key = request.session.get('file_name', '')
    print("File name5:", safe_image_key)
    
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    detect_image = s3.get_object(Bucket="nomercybucket", Key=safe_image_key)
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

                    email_message.attach(safe_image_key.split("/")[-1], image_data, 'image/jpg')

                    email_message.send(fail_silently=False)

                    result = JsonResponse({'message': '이메일이 성공적으로 전송되었습니다.'})
                except Exception as e:
                    print(f"이메일 전송 오류: {str(e)}")
                    result = JsonResponse({'error': str(e)}, status=500)
    return result

# 처리된 파일을 다운로드하는 함수
def download(request):
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    safe_image_key = request.session.get('file_name', '')

    desktop_path = os.path.join(os.path.expanduser("~"), 'Desktop')

    local_file_path = os.path.join(desktop_path, safe_image_key.split('/')[-1])

    with open(local_file_path, 'wb') as local_file:
        s3.download_fileobj("nomercybucket", safe_image_key, local_file)

    return HttpResponse("File downloaded successfully.")
