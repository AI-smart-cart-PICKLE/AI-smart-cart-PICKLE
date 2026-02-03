import mlflow.store.db.utils
from sqlalchemy import create_engine
engine = create_engine('postgresql://admin:password123@db:5432/mlflow')
mlflow.store.db.utils._initialize_tables(engine)
print("MLflow database initialized successfully.")