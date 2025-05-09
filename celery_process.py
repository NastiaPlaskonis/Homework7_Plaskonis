from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def process_data(data):
    
    print(f"[CELERY] Processing data... {data}")
    return {"processed": True, "original": data}