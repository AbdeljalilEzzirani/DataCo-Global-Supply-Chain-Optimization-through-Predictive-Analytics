# DataCo-Global-Supply-Chain-Optimization-through-Predictive-Analytics
Optimisation de la Supply Chain de DataCo Global par l'Analyse Prédictive

  # zookeeper:
  #   image: confluentinc/cp-zookeeper:7.3.0
  #   ports:
  #     - "2181:2181"
  #   environment:
  #     ZOOKEEPER_CLIENT_PORT: 2181
  #     ZOOKEEPER_TICK_TIME: 2000
  #     ZOOKEEPER_LOG4J_LOGGERS: "org.apache.zookeeper=DEBUG"
  #   healthcheck:
  #     test: ["CMD", "bash", "-c", "echo 'ruok' | nc -w 2 localhost 2181 | grep imok"]
  #     interval: 10s
  #     timeout: 10s
  #     retries: 5
  #     start_period: 45s
  #   networks:
  #     - app-network
  #   deploy:
  #     resources:
  #       limits:
  #         cpus: '0.5'
  #         memory: 1G
  # kafka:
  #   image: confluentinc/cp-kafka:7.3.0
  #   ports:
  #     - "9092:9092"
  #   hostname: kafka
  #   container_name: kafka
  #   environment:
  #     KAFKA_BROKER_ID: 1
  #     KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
  #     KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
  #     KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT
  #     KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
  #     KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
  #     KAFKA_LOG4J_LOGGERS: "org.apache.kafka=DEBUG,org.apache.zookeeper=DEBUG"
  #   depends_on:
  #     zookeeper:
  #       condition: service_healthy
  #   # healthcheck:
  #   #   test: ["CMD", "kafka-topics.sh", "--list", "--bootstrap-server", "kafka:9092"]
  #   #   interval: 10s
  #   #   timeout: 10s
  #   #   retries: 5
  #   #   start_period: 240s
  #   # healthcheck:
  #   #   test: ["CMD", "kafka-topics.sh", "--list", "--bootstrap-server", "kafka:9092"]
  #   #   interval: 10s
  #   #   timeout: 10s
  #   #   retries: 5
  #   #   start_period: 60s
  #   volumes:
  #     - kafka-data:/var/lib/kafka/data
  #   networks:
  #     - app-network
  #   deploy:
  #     resources:
  #       limits:
  #         cpus: '1.0'
  #         memory: 4G
  #   restart: on-failure:3
  #   entrypoint: |
  #     sh -c "
  #       # Start Kafka in background
  #       /etc/confluent/docker/run &
  #       # Wait for Kafka to be ready
  #       until kafka-topics.sh --bootstrap-server kafka:9092 --list > /dev/null 2>&1; do
  #         echo 'Waiting for Kafka to start...'; sleep 5;
  #       done
  #       # Create test topic
  #       kafka-topics.sh --create \
  #         --topic test \
  #         --bootstrap-server kafka:9092 \
  #         --partitions 1 \
  #         --replication-factor 1 \
  #         --if-not-exists;
  #       # Wait for background process
  #       wait
  #     "



  # grafana:
  #   image: grafana/grafana:10.0.0
  #   ports:
  #     - "3000:3000"
  #   volumes:
  #   networks:
  #     - app-network
  #     - grafana-data:/var/lib/grafana



<!-- 

version: '3.8'
services:
  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: mlflow
      POSTGRES_PASSWORD: mlflow
      POSTGRES_DB: mlflow
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "mlflow"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - app-network

  airflow:
    image: apache/airflow:2.10.5
    ports:
      - "8080:8080"
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/requirements.txt:/opt/airflow/requirements.txt
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://mlflow:mlflow@postgres/mlflow
      - AIRFLOW__CORE__FERNET_KEY=OJ2m6N7Y3z8W9kQvT5LxP1rF4uJ0eG2hD9iC8bA5mB=
    depends_on:
      postgres:
        condition: service_healthy
    command: bash -c "sleep 30 && pip install -r /opt/airflow/requirements.txt && airflow db init && airflow webserver & airflow scheduler" #update
    env_file:
      - .env
    networks:
      - app-network
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G


  airflow:
      build:
        context: ./airflow
        dockerfile: Dockerfile
      ports:
        - "8080:8080"
      volumes:
        - ./airflow/dags:/opt/airflow/dags
        - ./airflow/requirements.txt:/opt/airflow/requirements.txt
        - ./airflow/airflow_init.sh:/tmp/airflow_init.sh
      environment:
        - AIRFLOW__CORE__EXECUTOR=LocalExecutor
        - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://mlflow:mlflow@postgres/mlflow
        - AIRFLOW__CORE__FERNET_KEY=OJ2m6N7Y3z8W9kQvT5LxP1rF4uJ0eG2hD9iC8bA5mB=
      depends_on:
        postgres:
          condition: service_healthy
      command: bash -c "cp /tmp/airflow_init.sh /tmp/airflow_init.sh.tmp && chmod +x /tmp/airflow_init.sh.tmp && /tmp/airflow_init.sh.tmp || (echo 'Initialization failed, keeping container alive for debugging...' && tail -f /dev/null)"
      env_file:
        - .env
      networks:
        - app-network
      healthcheck:
        test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
        interval: 30s
        timeout: 10s
        retries: 5
        start_period: 120s
      deploy:
        resources:
          limits:
            cpus: '1.0'
            memory: 5G


  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - app-network

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    hostname: kafka
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    networks:
      - app-network
    healthcheck:
      test: [ "CMD", "kafka-topics", "--bootstrap-server", "localhost:9092", "--list" ]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 120s #update
    volumes: #update
      - kafka-data:/var/lib/kafka/data #update
    entrypoint: |
      sh -c "
        # Start Kafka in background
        /etc/confluent/docker/run &
        # Wait for Kafka to be up (you might need to adjust the sleep duration)
        echo 'Waiting for Kafka to start...'; sleep 15;
        # Create Kafka topic
        kafka-topics --create \
          --topic logs \
          --bootstrap-server localhost:9092 \
          --partitions 1 \
          --replication-factor 1;
        # Wait for background process to end
        wait
      "
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    ports:
      - "8081:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: dataco-kafka
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
    depends_on:
      - kafka
    networks:
      - app-network

  mlflow:
    image: ghcr.io/mlflow/mlflow:v2.9.0
    ports:
      - "5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
    # command: mlflow server --backend-store-uri postgresql://mlflow:mlflow@postgres/mlflow --default-artifact-root ./mlruns
    command: bash -c "sleep 30 && mlflow server --backend-store-uri postgresql://mlflow:mlflow@postgres/mlflow --default-artifact-root ./mlruns"
    volumes:
      - ./mlflow/mlruns:/mlruns
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000"]
      interval: 30s
      timeout: 10s
      retries: 3
    env_file:
      - .env
    networks:
      - app-network
    #update
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G


  streamlit:
    build:
      context: ./streamlit
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
    volumes:
      - ./streamlit:/app
    env_file:
      - .env
    networks:
      - app-network



  dbt:
    build:
      context: ./dbt
      dockerfile: Dockerfile
    volumes:
      - ./dbt:/dbt
    depends_on:
      # - postgres
      postgres:
        condition: service_healthy
    env_file:
      - .env
    command: dbt run
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres-data:
  grafana-data:
  kafka-data: -->




# version: '3.8'
# services:
#   # PostgreSQL for Airflow, MLflow, and DBT
#   postgres:
#     image: postgres:13
#     environment:
#       POSTGRES_USER: ${POSTGRES_USER:-airflow}
#       POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-airflow}
#       POSTGRES_DB: airflow
#     volumes:
#       - postgres_data:/var/lib/postgresql/data
#     healthcheck:
#       test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER:-airflow}"]
#       interval: 10s
#       timeout: 5s
#       retries: 5
#       start_period: 30s
#     ports:
#       - "5432:5432"
#     networks:
#       - data_co_global_network

#   # Zookeeper for Kafka
#   zookeeper:
#     image: confluentinc/cp-zookeeper:7.3.0
#     environment:
#       ZOOKEEPER_CLIENT_PORT: 2181
#       ZOOKEEPER_TICK_TIME: 2000
#     ports:
#       - "2181:2181"
#     volumes:
#       - zookeeper_data:/data
#       - zookeeper_logs:/datalog
#     healthcheck:
#       test: ["CMD", "nc", "-z", "localhost", "2181"]
#       interval: 10s
#       timeout: 5s
#       retries: 3
#     networks:
#       - data_co_global_network

#   # Kafka
#   kafka:
#     image: confluentinc/cp-kafka:7.3.0
#     depends_on:
#       zookeeper:
#         condition: service_healthy
#     environment:
#       KAFKA_BROKER_ID: 1
#       KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
#       KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
#       KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT
#       KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
#       KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
#       KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
#       KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
#       KAFKA_NUM_PARTITIONS: 3
#       KAFKA_DEFAULT_REPLICATION_FACTOR: 1
#     ports:
#       - "9092:9092"
#     volumes:
#       - kafka_data:/var/lib/kafka/data
#     healthcheck:
#       test: ["CMD", "kafka-topics", "--list", "--bootstrap-server", "kafka:9092"]
#       interval: 10s
#       timeout: 5s
#       retries: 3
#       start_period: 30s
#     command: >
#       bash -c "sleep 10 && /etc/confluent/docker/run"
#     dns:
#       - 8.8.8.8
#       - 8.8.4.4
#     networks:
#       - data_co_global_network

#   # Airflow Initialization
#   airflow-init:
#     build:
#       context: ./airflow
#       dockerfile: Dockerfile
#     depends_on:
#       postgres:
#         condition: service_healthy
#     environment:
#       AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://${POSTGRES_USER:-airflow}:${POSTGRES_PASSWORD:-airflow}@postgres:5432/airflow
#       AIRFLOW__CORE__EXECUTOR: LocalExecutor
#       AIRFLOW__CORE__LOAD_EXAMPLES: "false"
#       AIRFLOW__CORE__FERNET_KEY: "UMqbFMaIOregWLoOE0Y4R9RJLhEZC1L9q7QRoSBCO10="
#     volumes:
#       - ./airflow/dags:/opt/airflow/dags:ro
#       - ./airflow/requirements.txt:/opt/airflow/requirements.txt
#       - ./airflow/airflow_init.sh:/tmp/airflow_init.sh
#     command: bash -c "cp /tmp/airflow_init.sh /tmp/airflow_init.sh.tmp && chmod +x /tmp/airflow_init.sh.tmp && /tmp/airflow_init.sh.tmp || (echo 'Initialization failed, keeping container alive for debugging...' && tail -f /dev/null)"
#     dns:
#       - 8.8.8.8
#       - 8.8.4.4
#     networks:
#       - data_co_global_network

#   # Airflow Webserver
#   airflow-webserver:
#     build:
#       context: ./airflow
#       dockerfile: Dockerfile
#     depends_on:
#       airflow-init:
#         condition: service_completed_successfully
#       postgres:
#         condition: service_healthy
#       kafka:
#         condition: service_healthy
#     environment:
#       AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://${POSTGRES_USER:-airflow}:${POSTGRES_PASSWORD:-airflow}@postgres:5432/airflow
#       AIRFLOW__CORE__EXECUTOR: LocalExecutor
#       AIRFLOW__CORE__LOAD_EXAMPLES: "false"
#       AIRFLOW__WEBSERVER__SECRET_KEY: "your-secret-key-for-airflow"
#       AIRFLOW__CORE__FERNET_KEY: "UMqbFMaIOregWLoOE0Y4R9RJLhEZC1L9q7QRoSBCO10="
#     volumes:
#       - ./airflow/dags:/opt/airflow/dags:ro
#       - ./airflow/requirements.txt:/opt/airflow/requirements.txt
#     ports:
#       - "8080:8080"
#     command: /home/airflow/.local/bin/airflow webserver -p 8080
#     healthcheck:
#       test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
#       interval: 30s
#       timeout: 10s
#       retries: 5
#       start_period: 60s
#     dns:
#       - 8.8.8.8
#       - 8.8.4.4
#     networks:
#       - data_co_global_network

#   # Airflow Scheduler
#   airflow-scheduler:
#     build:
#       context: ./airflow
#       dockerfile: Dockerfile
#     depends_on:
#       airflow-init:
#         condition: service_completed_successfully
#       postgres:
#         condition: service_healthy
#       kafka:
#         condition: service_healthy
#     environment:
#       AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://${POSTGRES_USER:-airflow}:${POSTGRES_PASSWORD:-airflow}@postgres:5432/airflow
#       AIRFLOW__CORE__EXECUTOR: LocalExecutor
#       AIRFLOW__CORE__LOAD_EXAMPLES: "false"
#       AIRFLOW__CORE__FERNET_KEY: "UMqbFMaIOregWLoOE0Y4R9RJLhEZC1L9q7QRoSBCO10="
#     volumes:
#       - ./airflow/dags:/opt/airflow/dags:ro
#       - ./airflow/requirements.txt:/opt/airflow/requirements.txt
#     command: /home/airflow/.local/bin/airflow scheduler
#     healthcheck:
#       test: ["CMD-SHELL", "ps aux | grep '[a]irflow scheduler'"]
#       interval: 30s
#       timeout: 10s
#       retries: 5
#       start_period: 60s
#     dns:
#       - 8.8.8.8
#       - 8.8.4.4
#     networks:
#       - data_co_global_network

#   # MLflow
#   mlflow:
#     build:
#       context: ./mlflow
#       dockerfile: Dockerfile
#     depends_on:
#       postgres:
#         condition: service_healthy
#     ports:
#       - "5000:5000"
#     command: >
#       bash -c "sleep 30 && pip install psycopg2-binary && mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri postgresql://airflow:airflow@postgres:5432/mlflow --default-artifact-root /mlruns"
#     volumes:
#       - ./mlflow/mlruns:/mlruns
#     healthcheck:
#       test: ["CMD", "curl", "-f", "http://localhost:5000"]
#       interval: 30s
#       timeout: 10s
#       retries: 3
#       start_period: 60s
#     networks:
#       - data_co_global_network

#   # Streamlit
#   streamlit:
#     build:
#       context: ./streamlit
#       dockerfile: Dockerfile
#     ports:
#       - "8501:8501"
#     command: python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
#     depends_on:
#       kafka:
#         condition: service_healthy
#     networks:
#       - data_co_global_network

#   # DBT
#   dbt:
#     build:
#       context: ./dbt
#       dockerfile: Dockerfile
#     volumes:
#       - ./dbt:/dbt
#     command: dbt run
#     depends_on:
#       postgres:
#         condition: service_healthy
#     environment:
#       DBT_PROFILES_DIR: /dbt
#     networks:
#       - data_co_global_network

#   # Kafka-UI
#   kafka-ui:
#     image: provectuslabs/kafka-ui:latest
#     ports:
#       - "8081:8080"
#     environment:
#       KAFKA_CLUSTERS_0_NAME: dataco-kafka
#       KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:9092
#       KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
#     depends_on:
#       kafka:
#         condition: service_healthy
#       zookeeper:
#         condition: service_healthy
#     networks:
#       - data_co_global_network

#   # Logistics API (FastAPI)
#   logistics-api:
#     build:
#       context: ./fastapi
#       dockerfile: Dockerfile
#     depends_on:
#       kafka:
#         condition: service_healthy
#     environment:
#       KAFKA_BOOTSTRAP_SERVERS: kafka:9092
#     ports:
#       - "8000:8000"
#     command: >
#       uvicorn main:app --host 0.0.0.0 --port 8000
#     healthcheck:
#       test: ["CMD", "curl", "--fail", "http://localhost:8000/health"]
#       interval: 30s
#       timeout: 10s
#       retries: 3
#       start_period: 30s
#     dns:
#       - 8.8.8.8
#       - 8.8.4.4
#     networks:
#       - data_co_global_network

#   # Grafana
#   grafana:
#     image: grafana/grafana:10.0.0
#     environment:
#       GF_AUTH_ANONYMOUS_ENABLED: "true"
#       GF_AUTH_ANONYMOUS_ORG_ROLE: Viewer
#     ports:
#       - "3000:3000"
#     volumes:
#       - ./visualization/grafana/dashboards:/var/lib/grafana/dashboards:ro
#       - grafana_data:/var/lib/grafana
#     healthcheck:
#       test: ["CMD", "curl", "--fail", "http://localhost:3000/api/health"]
#       interval: 30s
#       timeout: 10s
#       retries: 3
#     networks:
#       - data_co_global_network

#   # Kafka to Snowflake Consumer
#   kafka-to-snowflake:
#     build:
#       context: ./consumer
#       dockerfile: Dockerfile
#     depends_on:
#       kafka:
#         condition: service_healthy
#     environment:
#       SNOWFLAKE_ACCOUNT: "your_account.snowflakecomputing.com"
#       SNOWFLAKE_USER: "logistics_user"
#       SNOWFLAKE_PASSWORD: "your_secure_password"
#       KAFKA_BOOTSTRAP_SERVERS: kafka:9092
#     networks:
#       - data_co_global_network

# # Volumes for data persistence
# volumes:
#   postgres_data:
#   zookeeper_data:
#   zookeeper_logs:
#   kafka_data:
#   grafana_data:
#   mlruns:

# # Custom network for isolation
# networks:
#   data_co_global_network:
#     driver: bridge