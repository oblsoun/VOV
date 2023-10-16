function popOpen() {
    var modalWrap = document.querySelector('.modal-wrap');
    var modal = document.querySelector('.modal');
    modalWrap.style.display = 'block';
    modal.classList.remove('modal');
}
function popClose() {
    var modalWrap = document.querySelector('.modal-wrap');
    var modalNone = document.querySelector('.modal');
    modalWrap.style.display = 'none';
    modalNone.classList.add('modal');
}

// 라디오 버튼
document.addEventListener('DOMContentLoaded', function() {
    var radioButtons = document.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            if (this.checked) {
                // 다른 라디오 버튼의 선택 상태를 해제
                radioButtons.forEach(function(otherButton) {
                    if (otherButton !== button) {
                        otherButton.checked = false;
                    }
                });
            }
        });
    });
});

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

function enableEmailInput() {
    const radioButton1 = document.getElementById('radioButton1');
    const radioButton2 = document.getElementById('radioButton2');
    const emailInput = document.getElementById('email');
    const emailButton = document.querySelector('.email-button');
    const emailCheckSuccess = document.getElementById('email_check_success');
    
    if (radioButton1.checked) {
        emailInput.disabled = false;
        emailInput.style.visibility = 'visible'; // 이메일 입력 필드를 숨기지 않고 보이게 설정
        emailButton.style.display = 'inline-block';
        emailCheckSuccess.style.display = 'none';
    } else if (radioButton2.checked) {
        emailInput.disabled = true;
        emailInput.style.visibility = 'hidden'; // 이메일 입력 필드를 숨김
        emailInput.value = '';
        emailButton.style.display = 'none';
        emailCheckSuccess.style.display = 'none';
    }
}
document.getElementById('radioButton1').addEventListener('click', enableEmailInput);
document.getElementById('radioButton2').addEventListener('click', enableEmailInput);
document.getElementById('recordButton').addEventListener('click', popOpen);
document.getElementById('captureButton').addEventListener('click', popOpen);