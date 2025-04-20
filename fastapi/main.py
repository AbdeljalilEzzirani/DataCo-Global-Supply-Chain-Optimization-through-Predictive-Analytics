from fastapi import FastAPI
from kafka import KafkaProducer
import json
import datetime
import random
from faker import Faker

app = FastAPI()
producer = KafkaProducer(bootstrap_servers='kafka:9092')
fake = Faker()

warehouses = ['WH1', 'WH2', 'WH3', 'WH4']
destinations = ['Store1', 'Store2', 'Store3', 'DistributionCenter']
shipping_modes = ['Standard Class', 'Second Class', 'First Class', 'Same Day']

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/logistics")
async def send_logistics_data():
    order_data = {
        "order_id": f"ORD-{fake.uuid4().split('-')[0].upper()}",
        "departure_date": (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 5))).strftime('%Y-%m-%d'),
        "arrival_date": (datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d'),
        "quantity": random.randint(10, 500),
        "warehouse": random.choice(warehouses),
        "destination": random.choice(destinations),
        "shipping_mode": random.choice(shipping_modes),
        "order_amount": round(random.uniform(50.0, 5000.0), 2),
        "customer_id": f"CUST-{fake.uuid4().split('-')[0].upper()}",
        "late_delivery_risk": random.choice([0, 1])
    }
    producer.send('logs', json.dumps(order_data).encode('utf-8'))
    producer.flush()
    return {"status": "Data sent to Kafka", "data": order_data}