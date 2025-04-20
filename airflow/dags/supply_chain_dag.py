from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def collect_data():
    response = requests.get('http://logistics-api:8000/api/logistics')
    print(response.json())

with DAG(
    'supply_chain_dag',
    default_args=default_args,
    description='Collect logistics data and send to Kafka',
    schedule_interval='@hourly',
    start_date=datetime(2025, 4, 18),
    catchup=False,
) as dag:
    collect_task = PythonOperator(
        task_id='collect_data',
        python_callable=collect_data,
    )