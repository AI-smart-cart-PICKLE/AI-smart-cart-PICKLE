FROM apache/airflow:2.10.4

USER root
# 필요한 시스템 패키지가 있다면 여기에 추가 (예: gcc, git 등)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# 로컬 requirements.txt 복사 및 설치
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

