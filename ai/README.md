# AI & Edge (Jetson Orin Nano)

이 디렉토리는 **Jetson Orin Nano (Edge Device)** 및 모델 학습/전처리를 위한 AI 모듈을 관리합니다.



## 1. 디렉토리 구조

- **`inference/`**: YOLO 기반 객체 탐지 추론 서버 (FastAPI)
  - Jetson 및 로컬 개발 환경에서 실행 (`main.py`)
  - 추론 전 resizing 등 전처리 로직 포함
- **`preprocessing/`**: 이미지 전처리 및 증강(Augmentation) 로직
  - 로컬 개발환경에서 데이터셋 준비 시 사용
- **`training/`**: 모델 학습 스크립트
  - GPU 서버 또는 로컬에서 학습 시 사용
- **`Dockerfile`**: 통합 Dockerfile (로컬 테스트 및 Jetson 배포 겸용)
- **`environment.yaml`**: Conda 환경 설정 파일 (안정성 위주 설정)



## 2. 개발 환경

- **Python**: 3.10.19
- **Framework**
  - PyTorch 2.3.1
  - Ultralytics 8.4.2 (YOLOv8/v11)
- **Key Libraries**
  - numpy 1.26.4 (버전 고정)
  - opencv-python-headless 4.8
  - albumentations 1.4.10



## 3. 실행 가이드 (Local Development)

- `docker-compose`를 통해 실행
- 단, AI 추론 서버는 EC2 배포 시 제외되도록 설정되어 있으므로 로컬 개발 시 컨테이너를 실행할 때는 **`--profile dev`** 옵션이 필요



### 3.1. AI 서버 포함 전체 실행

로컬에서 AI 추론 서버(`localhost:8001`)까지 포함하여 전체 시스템을 테스트하려면 아래 명령어를 사용

```bash
# 루트 디렉토리에서 실행
docker compose --profile dev up --build -d
```

- 실행 후 접속: `http://localhost:8001/` (AI Inference Server)
- Swagger Docs: `http://localhost:8001/docs`

### 3.2. AI 서버 제외 실행 (기본)
AI 서버 없이 백엔드 및 인프라만 실행하려면 기본 명령어를 사용(EC2 배포 시 동작 방식)

```bash
docker compose up -d
```



## 4. Jetson 배포 참고

Jetson Orin Nano 환경에서는 `Dockerfile`의 베이스 이미지를 `dustynv/l4t-pytorch` 등으로 변경하거나, 해당 환경에 맞는 `runtime: nvidia` 설정을 추가하여 단독으로 실행해야 합니다.

