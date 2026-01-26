"""
의존성 및 환경 정상 동작 확인을 위한 단발성 추론 테스트 스크립트
- 모델 로딩
- 이미지 입력
- 추론 파이프라인 검증용
"""


from ultralytics import YOLO

model = YOLO("models/best.pt")
results = model("test.jpg", save=True)

for r in results:
    print("boxes (xyxy):", r.boxes.xyxy)
    print("classes:", r.boxes.cls)
    print("conf:", r.boxes.conf)
