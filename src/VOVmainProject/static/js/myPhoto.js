// 사용자가 체크박스를 선택할 때 function
document.addEventListener("DOMContentLoaded", function () {
    const checkboxes = document.querySelectorAll("input[type='checkbox']");
    const button1 = document.getElementById('save');
    const button2 = document.getElementById('delete');
    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener("click", function () {
            limitCheckboxes(checkboxes); // 최대 10개까지 선택 가능
            boxBorderChange(checkbox); // 선택하면 박스 스타일 변화
            handleButtons(checkboxes, button1, button2); // 1개라도 선택 시 버튼 활성화
        });
    });
});


// 체크하면 경계상자 변화
function boxBorderChange(checkbox) {
    const box = checkbox.closest(".box");
    if (checkbox.checked) {
        box.style.backgroundColor = "rgba(232, 239, 247, 0.5)";
        box.style.borderColor = "#3498db";
    } else {
        box.style.backgroundColor = "rgba(255, 255, 255, 1)";
        box.style.borderColor = "rgba(204, 204, 204, 1)";
    }
}


// 체크박스 10개 이하 선택
function limitCheckboxes(checkboxes) {
    var checkedCount = 0;
    for (var i = 0; i < checkboxes.length; i++) {
        var checkbox = checkboxes[i];
        if (checkbox.checked) {
            checkedCount++;
        }
        if (checkedCount > 10) {
            checkbox.checked = false;
            break;
        }
    }
    boxBorderChange(checkboxes[0]);
}


// 다운로드와 삭제 버튼 색 변화
function handleButtons(checkboxes, button1, button2) {
    var atLeastOneChecked = false;
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            atLeastOneChecked = true;
            break;
        }
    }
    if (atLeastOneChecked) {
        button1.disabled = false;
        button1.style.backgroundColor = "rgba(55,94,254,1)";
        button2.disabled = false;
        button2.style.backgroundColor = "rgba(255,255,255,1)";
    } else {
        button1.disabled = true;
        button1.style.backgroundColor = "rgba(169,169,169,1)";
        button2.disabled = true;
        button2.style.backgroundColor = "rgba(189,190,189,1)";
    }
}


//용량 표시
var progressValue = document.querySelector('.gb-text').getAttribute('data-photo-volume');
// 게이지 바 증가 함수
function fillProgressBar(progressValue) {
    progressValue = progressValue*10;
    const progressBar = document.getElementById('progress');
    if (progressValue >= 0 && progressValue <= 100) {
      progressBar.style.width = progressValue + '%';
      
      if (progressValue < 70) {
        progressBar.style.backgroundColor = 'green';
      } else if (progressValue < 90) {
        progressBar.style.backgroundColor = 'yellow';
      } else {
        progressBar.style.backgroundColor = 'red';
      }
    } else {
      console.error('Percentage should be between 0 and 100.');
      console.log(progressValue)
    }
  }
// 용량 반영하기
  fillProgressBar(progressValue);
