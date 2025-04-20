#!/bin/bash
set -e

LOG_FILE="/tmp/init.log"
touch $LOG_FILE
chmod 666 $LOG_FILE
echo "Starting Airflow initialization..." | tee -a $LOG_FILE
sync

echo "Waiting for Postgres..." | tee -a $LOG_FILE
sleep 180
sync

echo "Testing Postgres connection..." | tee -a $LOG_FILE
pip install psycopg2-binary >> $LOG_FILE 2>&1 || {
  echo "Failed to install psycopg2-binary" | tee -a $LOG_FILE
  sync
  exit 1
}

echo "Checking Postgres availability with retries..." | tee -a $LOG_FILE
for attempt in {1..10}; do
  echo "Attempt $attempt/10 to check Postgres..." | tee -a $LOG_FILE
  if pg_isready -h postgres -U airflow -d airflow >> $LOG_FILE 2>&1; then
    echo "Postgres is ready!" | tee -a $LOG_FILE
    sync
    break
  else
    echo "Postgres not ready on attempt $attempt" | tee -a $LOG_FILE
    sync
    if [ $attempt -eq 10 ]; then
      echo "All attempts failed. Exiting..." | tee -a $LOG_FILE
      sync
      exit 1
    fi
    sleep 10
  fi
done

echo "Testing psycopg2 connection..." | tee -a $LOG_FILE
python -c "import psycopg2; conn = psycopg2.connect(host='postgres', user='airflow', password='airflow', dbname='airflow'); print('Connected to Postgres!'); conn.close()" >> $LOG_FILE 2>&1 || {
  echo "Failed to connect to Postgres with psycopg2. Detailed error:" | tee -a $LOG_FILE
  python -c "import psycopg2; conn = psycopg2.connect(host='postgres', user='airflow', password='airflow', dbname='airflow')" >> $LOG_FILE 2>&1 || true
  sync
  exit 1
}
sync

echo "Creating mlflow database if not exists..." | tee -a $LOG_FILE
psql -h postgres -U airflow -d postgres -c "CREATE DATABASE mlflow;" >> $LOG_FILE 2>&1 || {
  echo "mlflow database creation failed or already exists" | tee -a $LOG_FILE
  sync
}
sync

echo "Installing requirements..." | tee -a $LOG_FILE
pip install -r /opt/airflow/requirements.txt >> $LOG_FILE 2>&1 || {
  echo "Failed to install requirements.txt" | tee -a $LOG_FILE
  sync
  exit 1
}
sync

echo "Initializing database..." | tee -a $LOG_FILE
for attempt in {1..5}; do
  echo "Attempt $attempt/5 to initialize database..." | tee -a $LOG_FILE
  if airflow db init >> $LOG_FILE 2>&1; then
    echo "Database initialized successfully!" | tee -a $LOG_FILE
    sync
    break
  else
    echo "Failed to initialize database on attempt $attempt" | tee -a $LOG_FILE
    sync
    if [ $attempt -eq 5 ]; then
      echo "All attempts failed. Exiting..." | tee -a $LOG_FILE
      sync
      exit 1
    fi
    sleep 10
  fi
done

echo "Creating admin user..." | tee -a $LOG_FILE
airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin >> $LOG_FILE 2>&1 || {
  echo "Failed to create admin user" | tee -a $LOG_FILE
  sync
  exit 1
}
sync

echo "Airflow initialization complete!" | tee -a $LOG_FILE
sync
