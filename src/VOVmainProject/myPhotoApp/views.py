from django.shortcuts import render, redirect
from django.http import HttpResponse
from myPhotoApp.models import MyPhoto
from django.urls import reverse
from django.conf import settings
import shutil
import tempfile
import zipfile
import boto3
import os

# 로그인한 사용자의 사진들을 불러온다
def my_photo_list_up(request):
    user_id = request.session.get('user_id')
    if MyPhoto.objects.filter(userid=user_id).exists():
        photo_list = MyPhoto.objects.filter(userid=user_id)
        context = {'photo_list' : photo_list,
                'photo_volume' : sum_filevolume(user_id)}
        html = "myPhotoApp\\myPhoto.html"
    else:
        html = "myPhotoApp\\myPhoto_empty.html"
        context = {}
    return render(request, html, context)


# 로그인한 사용자의 내사진 총 용량을 구하고 GB로 변환한다
def sum_filevolume(user_id):
    photos = MyPhoto.objects.filter(userid=user_id)
    kilobytes_total = sum(photo.filevolume for photo in photos)
    gigabytes_total = kilobytes_total / 1024
    return round(gigabytes_total, 1)


# 어떤 버튼이 눌렸는지 확인한다 (삭제 혹은 저장)
def my_photo_button(request):
    flag = request.POST.__getitem__("flag")
    if flag == "download":
        page = "download"
    elif flag == "delete":
        page = "delete"
    return redirect(page)


# 선택한 사진 다운로드한다
def my_photo_save(request):
    mp_nums = request.POST.getlist('checkedImages')
    if len(mp_nums) == 1:
        s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        image = MyPhoto.objects.get(mpnum=mp_nums[0])
        parts = image.image.split(".com/")
        response = HttpResponse(content_type='image/jpg')
        response['Content-Disposition'] = 'attachment; filename={}'.format(image.filename)
        try:
            s3.download_fileobj('nomercybucket', parts[1], response)
        except Exception as e:
            print(e)
    else: 
        response = my_photo_save_zip(mp_nums)
    return response


# 사진을 압축해서 다운로드한다
def my_photo_save_zip(mp_nums):
    s3 = boto3.client('s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    temp_dir = tempfile.mkdtemp()
    zip_file_name = 'clear.zip'
    zip_file = os.path.join(temp_dir, zip_file_name)
    with zipfile.ZipFile(zip_file, 'w') as zipf:
        for mp_num in mp_nums:
            image = MyPhoto.objects.get(mpnum=mp_num)
            parts = image.image.split(".com/")
            image_name = parts[1]
            s3.download_file('nomercybucket', image_name, os.path.join(temp_dir, image.filename))
            print('nomercybucket', image_name)
            zipf.write(os.path.join(temp_dir, image.filename), arcname=image.filename)
    with open(zip_file, 'rb') as zipf:
        response = HttpResponse(zipf.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{zip_file_name}"'  
    os.remove(zip_file)
    shutil.rmtree(temp_dir)
    return response



# 선택한 사진을 삭제한다
def my_photo_delete(request):
    if request.method == 'POST':
        mp_nums = request.POST.getlist('checkedImages')
        images = MyPhoto.objects.filter(mpnum__in=mp_nums)
        s3 = boto3.client(
            's3',
            region_name='ap-northeast-2',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        for image in images:
            image.delete()
            s3.delete_object(Bucket='nomercybucket', Key=image.image)
    return redirect(reverse('myPhotoApp:myphoto'))
