from sklearn.ensemble import RandomForestClassifier
import mlflow
import mlflow.sklearn
import pandas as pd
import snowflake.connector
from os import environ

# Snowflake connection
conn = snowflake.connector.connect(
    user=environ['SNOWFLAKE_USER'],
    password=environ['SNOWFLAKE_PASSWORD'],
    account=environ['SNOWFLAKE_ACCOUNT'],
    warehouse=environ['SNOWFLAKE_WAREHOUSE'],
    database=environ['SNOWFLAKE_DATABASE'],
    schema=environ['SNOWFLAKE_SCHEMA']
)

# Fetch training data
df = pd.read_sql("SELECT quantity, distance, weather_score, traffic_score, is_late FROM orders", conn)
conn.close()

X_train = df[['quantity', 'distance', 'weather_score', 'traffic_score']]
y_train = df['is_late']

with mlflow.start_run():
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    mlflow.sklearn.log_model(model, "delay_model")
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", model.score(X_train, y_train))