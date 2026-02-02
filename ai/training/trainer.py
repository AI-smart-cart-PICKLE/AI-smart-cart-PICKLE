import os
import mlflow
from ultralytics import YOLO

class YOLOTrainer:
    def __init__(self, experiment_name: str, tracking_uri: str):
        """
        YOLO 모델 학습 및 MLflow 로깅을 담당하는 클래스
        """
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri
        
        # Windows 환경 OpenMP 충돌 방지
        os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
        
        # MLflow 초기화
        mlflow.set_tracking_uri(self.tracking_uri)
        mlflow.set_experiment(self.experiment_name)
        
        print(f"[Trainer] Initialized with URI: {self.tracking_uri}")
        print(f"[Trainer] Experiment: {self.experiment_name}")

    def run(self, 
            data_yaml: str,
            model_name: str = "yolov8s.pt",
            epochs: int = 50,
            imgsz: int = 640,
            batch: int = 16,
            device: str = "0",
            project_dir: str = "runs/train",
            run_name: str = "mlflow_run"):
        """
        학습 실행 메인 메서드
        """
        # 모델 로드
        print(f"[Trainer] Loading model: {model_name}")
        model = YOLO(model_name)

        # 안전장치: 이전 Run 종료
        if mlflow.active_run():
            mlflow.end_run()

        # MLflow Run 시작
        with mlflow.start_run() as run:
            print(f"[MLflow] Run ID: {run.info.run_id}")
            
            # 파라미터 로깅
            mlflow.log_params({
                "model": model_name,
                "data": data_yaml,
                "epochs": epochs,
                "imgsz": imgsz,
                "batch": batch,
                "device": device
            })

            print("[Trainer] Starting YOLO training...")
            
            # 학습 실행
            results = model.train(
                data=data_yaml,
                imgsz=imgsz,
                epochs=epochs,
                batch=batch,
                device=device,
                workers=0,  # Windows 호환성

                # Augmentation
                mosaic=1.0,
                mixup=0.2,
                fliplr=0.5,
                
                project=project_dir,
                name=run_name,
                exist_ok=True
            )

            # 결과 지표 로깅
            self._log_metrics(results)

            # 모델 아티팩트 업로드
            self._log_artifacts(results.save_dir)
            
            return run.info.run_id

    def _log_metrics(self, results):
        """
        YOLO 학습 결과 지표를 MLflow에 기록
        """
        metrics = {
            "mAP50": results.box.map50,
            "mAP50-95": results.box.map,
            "fitness": results.fitness,
        }
        mlflow.log_metrics(metrics)
        print(f"[MLflow] Logged metrics: {metrics}")

    def _log_artifacts(self, save_dir):
        """
        학습된 가중치와 이미지를 MLflow Artifact로 업로드
        """
        best_model_path = os.path.join(save_dir, "weights", "best.pt")
        
        if os.path.exists(best_model_path):
            print(f"[MLflow] Uploading model: {best_model_path}")
            mlflow.log_artifact(best_model_path, artifact_path="weights")
            
            # Confusion Matrix 등 결과 이미지 업로드
            confusion_matrix = os.path.join(save_dir, "confusion_matrix.png")
            if os.path.exists(confusion_matrix):
                mlflow.log_artifact(confusion_matrix, artifact_path="plots")
        else:
            print(f"[Warning] Best model not found at {best_model_path}")
