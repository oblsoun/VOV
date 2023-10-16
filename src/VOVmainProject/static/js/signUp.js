// 아이디 중복 체크
document.querySelector('.username_input').addEventListener('input', function() {
    document.querySelector('#id_check_success').style.display = 'none';
    document.querySelector('.id_overlap_button').style.display = 'block';
});
function id_overlap_check() {
    let usernameInput = document.querySelector('.username_input');
    if (!usernameInput.value) {
        alert('아이디를 입력해주세요.');
        return; 
    }
    if (!/^[a-zA-Z]+$/.test(usernameInput.value)) {
        alert('아이디는 영어로만 이루어져야 합니다.');
        return; // 아이디가 조건에 맞지 않으면 함수 종료
    }
    if (usernameInput.value.length > 0 && usernameInput.value.length < 4) {
        alert('아이디는 4글자 이상 입력하세요.');
        return; // 아이디가 4글자 미만이면 함수 종료
    } else {
        let id_overlap_input = document.querySelector('input[name="username"]');
        let xhr = new XMLHttpRequest();
        xhr.open('GET', '/user/check_userid/?username=' + id_overlap_input.value, true);
        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 400) {
                let data = JSON.parse(xhr.responseText);
                console.log(data['overlap']);
                if (data['overlap'] == "fail") {
                    alert("이미 존재하는 아이디 입니다.");
                    id_overlap_input.value = '';
                    id_overlap_input.focus();
                    let idCheckSuccess = document.querySelector('#id_check_success');
                    idCheckSuccess.style.display = 'none';
                    isUsernameValid = false;
                } else {
                    alert("사용가능한 아이디 입니다.");
                    let idCheckSuccess = document.querySelector('#id_check_success');
                    idCheckSuccess.style.display = 'block';
                    document.querySelector('.id_overlap_button').style.display = 'none';
                    isUsernameValid = true;
                }
            }
            checkPasswordMatch(); // 아이디 상태가 변경될 때마다 비밀번호 확인 다시 호출
        };
        xhr.send();
    }
}

// 이메일 전송
let isEmailSent = false; // 이메일 전송 여부를 저장하는 변수
function sendVerificationCode() {
    const email = document.getElementById("email").value;
    const csrf_token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    const emailButton = document.querySelector('.email-button');
    const emailCheckSuccess = document.getElementById('email_check_success');
    emailButton.style.display = 'inline-block';
    emailCheckSuccess.style.display = 'none';
    // 코드가 입력되지 않았을 경우
    if (!email) {
        alert("이메일을 입력해주세요.");
        return;
    }
    if (isEmailSent) {
        return; // 이미 이메일이 전송된 경우 아무것도 하지 않음
    }
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/user/send_email/", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.setRequestHeader("X-CSRFToken", csrf_token);
    xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 400) {
            const data = JSON.parse(xhr.responseText);
            if ('message' in data) {
                alert(data.message);
                emailButton.style.display = 'none';
                emailCheckSuccess.style.display = 'inline-block';
                isEmailSent = true; // 이메일 전송 성공 시 변수를 true로 설정
            } else if ('error' in data) {
                alert(data.error);
            }
        } else {
            alert("이메일 전송에 실패했습니다.");
        }
    };
    xhr.send("email=" + email);
}
// 입력값 변경 시 처리
document.getElementById("email").addEventListener("input", function () {
    isEmailSent = false; // 이메일이 변경되면 다시 전송 상태로 돌아가도록 변수를 false로 설정

    const successImage = document.getElementById('email_check_success');
    successImage.style.display = 'none'; // 이미지 숨기기

    const verifyButton = document.querySelector('.email-button');
    verifyButton.style.display = 'inline-block'; // 버튼 보이기
});

// 인증 번호 확인
let isCodeVerified = false; // 코드 확인 여부를 저장하는 변수
function checkVerificationCode() {
    const code = document.getElementById("code").value;
    // 코드가 입력되지 않았을 경우
    if (!code) {
        alert("코드를 입력해주세요.");
        return;
    }
    if (isCodeVerified) {
        return; // 이미 코드가 확인된 경우 아무것도 하지 않음
    }
    // 서버로 코드 일치 여부 확인 요청
    $.ajax({
        url: '/user/check_code/',
        data: {
            'code': code
        },
        dataType: 'json',
        success: function (data) {
            console.log("내가 입력한 코드 번호:", code); // 내가 입력한 코드 번호 출력
            console.log("메일로 받은 랜덤 코드 번호:", data['random_code']); // 메일로 받은 랜덤 코드 번호 출력
            if (data['match'] === "success") {
                alert("인증이 성공적으로 완료되었습니다!");
                const successImage = document.getElementById('code_check_success');
                successImage.style.display = 'inline-block'; // 이미지 보이기
                // 버튼 숨기기 (선택 사항)
                const verifyButton = document.getElementById('code_button');
                verifyButton.style.display = 'none'; // 버튼 숨기기
                isCodeVerified = true; // 이메일 전송 성공 시 변수를 true로 설정
            } else {
                alert("인증 코드를 다시 확인해주세요.");
            }
        }
    });
}
// 입력값 변경 시 처리
document.getElementById("code").addEventListener("input", function() {
    isCodeVerified = false; // 코드가 변경되면 다시 확인 상태로 돌아가도록 변수를 false로 설정
    const successImage = document.getElementById('code_check_success');
    successImage.style.display = 'none'; // 이미지 숨기기
    const verifyButton = document.querySelector('.code_button');
    verifyButton.style.display = 'inline-block'; // 버튼 보이기
});
// 이메일 입력 값 변경 시 처리
document.getElementById("email").addEventListener("input", function () {
    isCodeVerified = false; // 코드가 변경되면 다시 확인 상태로 돌아가도록 변수를 false로 설정
    const successImage = document.getElementById('code_check_success');
    successImage.style.display = 'none'; // 이미지 숨기기
    const verifyButton = document.querySelector('.code_button');
    verifyButton.style.display = 'inline-block';
});

function updateCategories() {
    let userType = document.getElementById("user_type").value;
    let companyCategories = document.getElementById("company_categories");
    let individualCategories = document.getElementById("individual_categories");

    if (userType === "기업") {
        companyCategories.style.display = "block";
        individualCategories.style.display = "none";
    } else if (userType === "개인") {
        companyCategories.style.display = "none";
        individualCategories.style.display = "block";
    }
}


// 회원 가입
function joinSubmit(event) {
    usernameInput = document.getElementById('username').value;
    if (usernameInput == '') {
        alert('아이디를 입력해주세요.');
        document.getElementById('username').focus();
        return false;
    }
    usernameBtn = document.querySelector('.id_check_success').style.display === 'block';
    if (!usernameBtn) {
        alert('중복검사를 해주세요.');
        document.getElementById('username').focus();
        return false;
    }
    passwordInput1 = document.getElementById('password').value;
    if (passwordInput1 == '') {
        alert('비밀번호를 입력해주세요.');
        document.getElementById('password').focus();
        return false;
    }
    passwordInput2 = document.getElementById('confirm_password').value;
    if (passwordInput2 == '') {
        alert('비밀번호 확인를 입력해주세요.');
        document.getElementById('confirm_password').focus();
        return false;
    }
    if(passwordInput1 != passwordInput2) {
        alert("비밀번호가 일치하지 않습니다.");
        document.getElementById('confirm_password').focus();
        return false;
    }
    nicknameInput = document.getElementById('nickname').value;
    if (nicknameInput == '') {
        alert('이름을 입력해주세요.');
        document.getElementById('nickname').focus();
        return false;
    }
    emailInput = document.getElementById('email').value;
    if (emailInput == '') {
        alert('이메일을 입력해주세요.');
        document.getElementById('email').focus();
        return false;
    }
    if (!isEmailSent) {
        alert('코드전송을 해주세요.');
        return false;
    }
    codeInput = document.getElementById('code').value;
    if (codeInput == '') {
        alert('코드를 입력해주세요');
        document.getElementById('code').focus();
        return false;
    }
    if (!isCodeVerified) {
        alert('코드확인을 해주세요');
        return false;
    }
    userTypeSelect = document.getElementById('user_type');
    userTypeValue = userTypeSelect.value;
    
    if (userTypeValue == '') {
        alert('사용자 유형을 선택해주세요.');
        userTypeSelect.focus();
        return false;
    }
    userCategorySelect = document.getElementById('user_category');
    userCategoryValue = userCategorySelect.value;
    
    if (userCategoryValue == '') {
        alert('사용자 구분을 선택해주세요.');
        userCategorySelect.focus();
        return false;
    }
    return true;
}

function updateCategories() {
    let userType = document.getElementById("user_type").value;
    let companyCategories = document.getElementById("company_categories");
    let individualCategories = document.getElementById("individual_categories");

    if (userType === "company") {
        companyCategories.style.display = "block";
        individualCategories.style.display = "none";
    } else if (userType === "individual") {
        companyCategories.style.display = "none";
        individualCategories.style.display = "block";
    }
}