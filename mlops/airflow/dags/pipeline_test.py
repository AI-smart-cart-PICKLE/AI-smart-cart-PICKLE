from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# 기본 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 정의
with DAG(
    '01_pipeline_integration_test',
    default_args=default_args,
    description='A dummy pipeline to test MLflow and MinIO integration',
    schedule_interval=None, # 수동 실행 (Manual Trigger)
    start_date=days_ago(1),
    tags=['mlops', 'test'],
    catchup=False,
) as dag:

    # Task 1: 환경 변수 및 의존성 확인 (Optional)
    check_env = BashOperator(
        task_id='check_environment',
        bash_command='echo "Checking MLflow connection..." && python --version && pip list | grep mlflow'
    )

    # Task 2: Mock Training Script 실행
    # Airflow Docker Container 내부 경로 기준: /opt/airflow/dags/scripts/mock_train.py
    run_mock_train = BashOperator(
        task_id='run_mock_training',
        bash_command='python /opt/airflow/dags/scripts/mock_train.py',
        env={
            # docker-compose network 내에서 MLflow 컨테이너 주소
            'MLFLOW_TRACKING_URI': 'http://mlflow_server:5000',
            # 필요한 경우 AWS Credential 등을 여기서 주입 가능하지만,
            # Docker Compose 레벨에서 이미 주입되어 있으면 생략 가능
            'AWS_ACCESS_KEY_ID': 'admin',
            'AWS_SECRET_ACCESS_KEY': 'password123',
            'MLFLOW_S3_ENDPOINT_URL': 'http://minio:9000'
        }
    )

    check_env >> run_mock_train
