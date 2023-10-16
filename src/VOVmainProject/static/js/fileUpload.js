document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("file");
    const fileListContainer = document.querySelector(".drop-zone");

    // 파일 선택(input type="file") 이벤트 처리
    fileInput.addEventListener("change", function () {
        const selectedFiles = fileInput.files;
        handleFiles(selectedFiles);
        fileInput.value = ""; // 파일 선택 후 input 요소 초기화
    });

    // 드래그 앤 드롭 이벤트 처리
    const dropZone = document.querySelector(".drop-zone");

    // 드래그 앤 드롭 영역 스타일을 변경하는 함수
    function highlightDropZone() {
        dropZone.classList.add("active");
    }

    function unhighlightDropZone() {
        dropZone.classList.remove("active");
    }

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault(); // 브라우저의 기본 동작 중지
        highlightDropZone();
    });

    dropZone.addEventListener("dragleave", () => {
        unhighlightDropZone();
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault(); // 브라우저의 기본 동작 중지
        unhighlightDropZone();
        const droppedFiles = e.dataTransfer.files;
        handleFiles(droppedFiles);
    });

    // 파일 처리 함수
    function handleFiles(fileList) {
        if (fileList.length > 10) {
            alert("10개까지만 파일을 업로드할 수 있습니다.");
            // 파일 개수가 10개를 초과하는 경우 처리 중단
            return;
        }

        // 파일 목록을 화면에 추가
        fileListContainer.innerHTML = ""; // 이전 파일 목록 지우기

        for (let i = 0; i < fileList.length; i++) {
            const file = fileList[i];
            const li = document.createElement("li");
            li.textContent = `${file.name} (${formatBytes(file.size)})`;
            fileListContainer.appendChild(li);
        }
    }

    // 파일 크기를 바이트에서 더 읽기 쉬운 단위로 포맷팅하는 함수
    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];

        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
});
