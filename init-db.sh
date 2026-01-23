#!/bin/bash
set -e

# $POSTGRES_DB (기본 DB)로 접속하여, 추가 DB들을 생성
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    
    -- 1. Airflow 메타데이터 저장소
    CREATE DATABASE airflow;
    
    -- 2. MLflow 실험 추적 저장소
    CREATE DATABASE mlflow;
    
    -- 3. App 비즈니스 로직 저장소
    CREATE DATABASE app_db;

EOSQL

# app_db에 접속하여 pgvector 확장 활성화 (벡터 검색 필수)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "app_db" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL
