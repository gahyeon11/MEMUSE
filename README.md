<div align="center">
        
![인스타-카드뉴스-001 (1) - 복사본](https://github.com/gahyeon11/AI_Image_with-voice/assets/117976216/91ca2edf-e57e-43af-ac6c-35f3544d63b5) 
![인스타-카드뉴스-001 (1) (1)](https://github.com/gahyeon11/AI_Image_with-voice/assets/117976216/13ea6d7c-cfba-4671-aa80-a1a65d27644f)

</div>

# Memuse
   
> 덕성여자대학교 IT미디어공학과
> 
> 개발기간 2023.06 ~ 2023.12
>
> 이가영, 박세연, 이시윤, 김가현, 손유빈
> 

## 프로젝트 소개

현존하는 대다수의 AI 서비스는 비장애인을 대상으로 만들어졌기에 신체적 제약이 존재하는 장애인은 서비스에 접근조차 어려운 경우가 대다수이다. 
특히, 최근 눈부신 기술 발전을 보이는 이미지 생성 AI 역시Text-to-Image 인공지능 모델을 기반으로 하여 텍스트의 입력이 필수적이다. 
때문에, 키보드나 마우스 같은 입력 장치를 사용하지 못하는 이들에게 있어 AI 활용의 장벽은 더욱 높아지고 있다.<br>
본 애플리케이션은 이러한 문제를 해결하기 위해 마우스와 키보드 없이도 음성 인식을 통해 서비스를 자유롭게 이용할 수 있도록 하였다. 
또한 디지털 기술에 취약한 이들도 디지털 이미지를 만들수 있도록 인공지능을 활용한 이미지 생성 기술에 접근하는 방법을 설명한다.<br>
본 애플리케이션은 음성 인식 기술인 STT(Speech To Text)의 개인별 활용과더불어 AI 이미지 생성 서비스가 겪고 있는 문제점인 예술 창의성 지표를 높이는 것을 목적으로 하였다. STT로 기록된 텍스트는 번역 API를 통해 한 번 더 가공된다. 
창작 이미지 생성에는 생성형 AI 모델 중스테이블 디퓨전 (Stable Diffusion)을 사용하였다. 
예술 창의성 지표를높이기 위한 방법으로 OpenCV를 이용해 이미지 수정 및 편집이 가능하도록 하였다. 
이 외에도 언리얼 엔진을 기반으로 한 메타버스 공간 구축및 콘텐츠 개발을 통해 대중의 접근성을 확장하고자 및 콘텐츠 개발을 통해 대중의 접근성을 확장하고자 한다.

## ABOUT

> 사용자는 본인이 원하는 화풍 뿐만 아니라 그림의 모든 부분을 직접 선택 가능 하다.
> <br> 사용자는 초보자, 전문가 단계 중 본인의 수준에 맞는 단계를 선택한다.
> <br> 초보자 단계의 모든 과정은 선택지로 부여되어 번호 선택만으로 손쉽게 그림을 생성할 수 있다.
> <br> 전문가 단계는 선택지 뿐만 아니라 직접 자신만의 문장으로 프롬프트를 적어볼 수 있다. 자신의 문장을 그림으로 만나보는 경험을 할 수 있다. 
> <br> 뿐만 아니라 배경과 분리된 별도의 사물 이미지를 생성하고 이를 조정, 편집하는 과정에서 본인의 자유도가 추가된 그림을 만들어볼 수 있다. 
> <br> 완성된 그림, 다른 사용자의 그림은 웹 페이지 상에서도 확인 가능하며, 언리얼로 구성된 두가지 테마의 가상 전시관을 통해서도 확인할 수 있다.

### 모든 단계는 음성, 마우스 모두 동작
#### 메인페이지
<br>

![메인 1-1](https://github.com/user-attachments/assets/6b221e5f-160a-4dba-860d-e2d1fad19e1b)

![메인 1-4](https://github.com/user-attachments/assets/4931653b-2bb6-4497-910d-8da5a6be9995)

#### 로그인 / 회원가입
<br>

![음성 인식 사용자 - 로그인](https://github.com/user-attachments/assets/a9cf8212-4a17-47c2-8f28-ecce302c022c)
![회원가입 선택](https://github.com/user-attachments/assets/96b5c832-172d-4ec9-b77d-2429f7055098)
![음성 인식 사용자 - 회원가입3](https://github.com/user-attachments/assets/2d30225b-85f6-45c3-8aab-4679ec6b6065)
![음성 인식 사용자 - 회원가입1](https://github.com/user-attachments/assets/5b0aeb4f-dca0-4d27-8f0f-0e277d4701ce)

<br>

#### 이미지 생성 - 초보자

1. 배경, 오브젝트 이미지 종류 선택
2. 선택된 종류 내에서 랜덤 생성

<br>

![스크린샷 2024-11-05 162430](https://github.com/user-attachments/assets/74f8967a-e93c-4722-b8ad-ef1ad287af7e)


<br>

#### 이미지 생성 - 전문가 

1. 화충, 그림 스타일, 보정 정도 선택
2. 배경, 오브젝트의 프롬프트 직접 입력
3. 이미지 추가, 삭제, 위치/크기 수정 등을 통하여 이미지 커스텀
4. 필터 적용
5. 커스텀 이미지 생성

<br>

![스크린샷 2024-11-05 162922](https://github.com/user-attachments/assets/c3067287-da07-40f8-a558-3d3e738189e9)
![스크린샷 2024-11-05 163008](https://github.com/user-attachments/assets/46f84df2-f8cc-4eef-9339-f745f9183bc2)
![스크린샷 2024-11-05 163036](https://github.com/user-attachments/assets/d3f6f174-ea51-421b-b2dd-ab4a2dd4d257)


<br>

#### 갤러리 내에서 확인
- 웹 페이지 내의 갤러리 뿐만 아니라 언리얼엔진을 이용해 제작된 가상의 전시관을 통해서도 자신의 그림 / 다른 사용자의 그림 감상이 가능하다.
- 가상 공간 전시관은 기본 / 바다 두가지 테마로 제작되어 다양하게 이용 가능하다.
<br>

![스크린샷 2024-11-05 164309](https://github.com/user-attachments/assets/8230d896-912e-47eb-9a4b-fe1a30cef7b0)

![스크린샷 2024-11-05 163427](https://github.com/user-attachments/assets/235b8521-1041-44f8-8a14-6108ee22e0a1)

![스크린샷 2024-11-05 163135](https://github.com/user-attachments/assets/3dff68b9-916b-46ed-a450-f0660ab9162d)

---

![image](https://github.com/gahyeon11/AI_Image_with-voice/assets/117976216/6bc8115b-9841-4638-a51c-80bbcce48779)


<div align=center><h1>📚 STACKS</h1></div>

<div align=center> 

  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> 
<br>
 <img src="https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white">
 <img src="https://img.shields.io/badge/css-1572B6?style=for-the-badge&logo=css3&logoColor=white">
 <img src="https://img.shields.io/badge/javascript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"> 
 <br>
  <img src="https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white">
  <br>
   <img src="https://img.shields.io/badge/react-61DAFB?style=for-the-badge&logo=react&logoColor=black"> 
  <img src="https://img.shields.io/badge/vue.js-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white"> 
  <img src="https://img.shields.io/badge/node.js-339933?style=for-the-badge&logo=Node.js&logoColor=white">
  <br>
  <img src="https://img.shields.io/badge/flask-000000?style=for-the-badge&logo=flask&logoColor=white">
  <br>
   <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white">
  <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white">
  <br>
  <img src="https://img.shields.io/badge/unreal-0E1128?style=for-the-badge&logo=unreal&logoColor=white">
  <br>
  </div>
