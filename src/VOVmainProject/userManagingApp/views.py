from django.shortcuts import render, redirect
from userManagingApp.models import User
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
import random
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

LOGIN_TEMPLATE = 'userManagingApp/logIn.html'
def login_view(request):
    result = None
    if request.method == "POST":
        # 폼에서 입력받은 아이디와 비밀번호를 가져옵니다.
        user_id = request.POST.get('username')
        user_password = request.POST.get('password')
        try:
            # 사용자 조회
            user = User.objects.get(userid=user_id)
            # 비밀번호 확인
            if user.userpassword == user_password:
                # 세션 데이터 설정 예시 (세션 ID 및 이메일)
                request.session['user_id'] = user.userid
                request.session['user_email'] = user.useremail
                request.session['user_name'] = user.username 
                result = redirect('fileUpload')  # 로그인 성공 시 리디렉션
            else:
                # 비밀번호 불일치 시 처리
                error_message = "비밀번호가 일치하지 않습니다."
                result = render(request, LOGIN_TEMPLATE, {'error_message': error_message})
        except User.DoesNotExist:
            # 사용자가 존재하지 않는 경우 처리
            error_message = "존재하지 않는 아이디입니다. 다시 확인해주세요."
            result = render(request, LOGIN_TEMPLATE, {'error_message': error_message})
    else:
        # POST 요청이 아닌 경우, 즉 GET 요청이나 다른 요청에 대한 처리
        result = render(request, LOGIN_TEMPLATE)
    return result

# 로그인 후 메인페이지 이동
def file_upload_log(request):
    # 세션에서 값을 가져옴
    user_id = request.session.get('user_id')
    user_email = request.session.get('user_email')
    # 가져온 값을 context에 추가
    context = {'user_id': user_id, 'user_email': user_email}
    return render(request, 'fileDeidentificationApp/fileUpload.html', context)

# 로그아웃 후 메인페이지 이동
def logout_view(request):
    del request.session['user_id']
    del request.session['user_email']
    return redirect('fileUpload')  # 로그아웃 후 메인 페이지로 리다이렉션

# 회원가입
@csrf_exempt
def sign_up(request):
    result = None 
    if request.method == 'POST':
        user_id = request.POST.get('username')
        user_password = request.POST.get('password')
        user_name = request.POST.get('nickname')
        user_email = request.POST.get('email')
        user_type = request.POST.get('user_type')
        user_category = request.POST.get('user_category')
        # 필수 필드 확인
        if not (user_id and user_password and user_name and user_email and user_type and user_category):
            error_message = 'Please provide all required fields.'
            result = render(request, 'userManagingApp/signUp.html', {'error_message': error_message})
        else:
            # 사용자 생성
            user = User(
                userid=user_id,
                userpassword=user_password,
                username=user_name,
                useremail=user_email,
                userclass1=user_type,
                userclass2=user_category,
                socialuser=0
            )
            user.save()
            # 세션 저장
            request.session['user_id'] = user.userid
            request.session['user_email'] = user.useremail
            request.session['user_name'] = user.username 
            result = redirect('fileUpload')
    if result is None:
        result = render(request, 'userManagingApp/signUp.html')
    return result

# 아이디 중복 검사
def id_overlap_check(request):
    user_id = request.GET.get('username')
    overlap = "pass"
    try:
        User.objects.get(userid=user_id)
        overlap = "fail"
    except User.DoesNotExist:
        pass
    context = {'overlap': overlap}
    return JsonResponse(context)

# 이메일 전송
@csrf_exempt
def send_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        result = None
        if not email:
            result = JsonResponse({'error': '이메일 주소를 입력해주세요.'}, status=400)
        else:
            random_number = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            request.session['random_code'] = random_number
            try:
                send_mail(
                    "[VOV] 인증 코드 전송 메일입니다.",
                    f"인증 코드: {random_number}",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                result = JsonResponse({'message': '이메일이 성공적으로 전송되었습니다.'})
            except Exception as e:
                print(f"이메일 전송 오류: {str(e)}")
                result = JsonResponse({'error': str(e)}, status=500)
    else:
        result = JsonResponse({'error': '올바르지 않은 요청입니다.'}, status=405)
    return result
        
# 인증 코드 확인
def check_code(request):
    result = None
    if request.method == 'GET':
        code = request.GET.get('code')
        # 저장된 랜덤 코드 번호 불러오기
        random_code = request.session.get('random_code')
        if code == random_code:
            result = JsonResponse({'match': 'success'})
        else:
            result = JsonResponse({'match': 'fail'})
    else:
        result = JsonResponse({'error': 'Invalid request method'}, status=405)
    return result

# 마이페이지 내정보조회
def show_mypage(request):
   # 세션에서 값을 가져옴
    user_id = request.session.get('user_id')
    user_email = request.session.get('user_email')
    user_name = request.session.get('user_name')
    context = {'user_id': user_id, 'user_email': user_email, 'user_name': user_name}
    return render(request, 'userManagingApp/myPage.html', context)