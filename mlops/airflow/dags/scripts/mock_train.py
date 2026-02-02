import mlflow
import os
import random
import time
import sys

# Airflow 컨테이너 내부에서 실행될 때 MLflow 서버 주소
# docker-compose.yml의 service name 또는 container_name을 사용
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow_server:5000")

def train_mock_yolo():
    print(f"Connecting to MLflow at: {MLFLOW_TRACKING_URI}")
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    # Experiment 설정 (없으면 생성)
    experiment_name = "YOLO_Mock_Training"
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=f"mock_run_{int(time.time())}"):
        print("Starting Mock Training...")
        
        # 1. 하이퍼파라미터 로깅 (Pre-defined params)
        params = {
            "model_type": "yolov8s",
            "epochs": 50,
            "batch_size": 16,
            "img_size": 640,
            "optimizer": "SGD"
        }
        mlflow.log_params(params)
        print("Logged parameters.")

        # 2. 학습 루프 시뮬레이션 (Metrics logging)
        for epoch in range(1, 11):
            # 학습 진행 척 하기
            time.sleep(0.5) 
            
            # 지표 생성 (점점 좋아지는 척)
            loss = 1.0 / (0.1 * epoch + 1) + random.uniform(-0.05, 0.05)
            map50 = 0.5 + (0.04 * epoch) + random.uniform(-0.01, 0.01)
            if map50 > 0.95: map50 = 0.95
            
            mlflow.log_metric("train_loss", loss, step=epoch)
            mlflow.log_metric("val_mAP50", map50, step=epoch)
            
            print(f"Epoch {epoch}/10 - loss: {loss:.4f} - mAP50: {map50:.4f}")

        # 3. 아티팩트(모델 파일) 저장 시뮬레이션
        # 실제로는 여기서 best.pt 파일이 생성됨
        os.makedirs("weights", exist_ok=True)
        dummy_weight_path = "weights/best.pt"
        with open(dummy_weight_path, "w") as f:
            f.write(f"This is a dummy YOLO weight file created at {time.ctime()}")
        
        # MLflow Artifact Store(MinIO)에 업로드
        mlflow.log_artifact(dummy_weight_path, artifact_path="models")
        print(f"Uploaded artifact: {dummy_weight_path}")

        print("Mock Training Complete.")

if __name__ == "__main__":
    try:
        train_mock_yolo()
    except Exception as e:
        print(f"Error during mock training: {e}")
        sys.exit(1)
