#  Frontend (Mobile & Kiosk)

이 디렉토리는 사용자 인터페이스(UI)를 담당하는 모바일 앱과 키오스크 웹 프로젝트를 포함합니다.



## 1. 디렉토리 구조

- **`mobile-app/`**: 사용자 스마트폰용 **Flutter** 프로젝트.
  - QR 스캔, 결제 내역 조회, 가계부 기능 제공.
  - 빌드 결과물: APK (Android), IPA (iOS).
- **`web-kiosk/`**: 스마트 카트 디스플레이용 **Vue.js** 웹 프로젝트.
  - 실시간 장바구니 목록, 추천 레시피, 결제 화면 제공.
  - Jetson 내부의 브라우저에서 실행됨.
- **`nginx/`**: 웹 프론트엔드(`web-kiosk`) 서빙 및 리버스 프록시 설정.



## 2. 개발 환경

- **Mobile**: Flutter 3.38.7 (Dart 3.10.7)
- **Web**: Vue.js 3.5.x, Node.js 22.x
- **Server**: Nginx (Docker Container)



## 3. 배포 가이드
