# :lock: 개인정보 비식별화 지원 서비스 개발

[![시연영상](http://img.youtube.com/vi/z_S71TbysyU/mqdefault.jpg)](https://youtu.be/z_S71TbysyU)

## :mag_right: 개요
- 프로젝트 목적
- 프로젝트 아이디어 및 배경
- 주요 기술
- 기술 스택
- 테이블 설계
- 기타 링크
- --
### :pushpin: 프로젝트 목적
##### 기획 의도
- AI 기반의 생체 정보 보안을 위한 지문 비식별화
- 개인정보 데이터 관리의 중요성 인식 확산
##### 프로젝트 내용
- 지문 영역 인지 및 지문 식별 정보 추출
- 추출된 지문 비식별화
- 후처리된 파일 저장 및 전송
---
### :bulb: 프로젝트 특장점
- Mediapipe 라이브러리 및 YOLOv5 모델로 높은 정확도와 빠른 속도로 지문 추출
- 기존 지문 인식 시스템의 부족한 보호 기능 보완
- 보안을 위해 후처리된 이미지만 데이터베이스만 저장
- 안정적인 AWS 인프라 및 다양한 산업 분야에서 활용 가능
- 사용자 친화적 환경으로 업로드 및 결과 처리 용이
---
### :star: 주요 기술
- Mediapipe 라이브러리를 사용하여 손 끝 위치를 감지
- [Custom YOLOv5 모델](https://colab.research.google.com/drive/1dKO153AU2HZRUqF23diTxx2qycikQkzL?usp=sharing)을 사용하여 지문 식별(mAP50 0.903)
- AWS 인프라를 활용한 무중단 배포와 S3, RDS를 이용한 데이터 저장 및 클라우드 서비스 제공
---
### :hammer: 기술 스택
- 서비스 구성도
  
![service](https://github.com/oblsoun/nomercy/assets/113246634/7b7d23ec-a8d5-4e17-a5bc-f3f92b2e4a4b)

- 메뉴 구성도

![menu](https://github.com/oblsoun/nomercy/assets/113246634/5e3f6af1-139f-4dc1-9fc1-dbf974e86096)
  
- UseCase

![usecase](https://github.com/oblsoun/nomercy/assets/113246634/677f3b93-11d4-4f00-8d6d-4c956a6b2802)

- 알고리즘 명세서
  
![model](https://github.com/oblsoun/nomercy/assets/113246634/ff895aaf-1013-4a5a-99fd-af69649b7b24)

---
### :date: 테이블 설계
![ERD](https://github.com/oblsoun/nomercy/assets/113246634/76dbc7e8-90e0-423d-9150-eeefe63b2fde)

---
### :paperclip: 기타 링크
[Custom Dataset - Roboflow](https://universe.roboflow.com/fingerprint-nze3i/vov-k9idv)

[활용 예시](https://github.com/oblsoun/safesnap)
