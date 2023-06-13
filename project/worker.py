from celery import Celery
import os

worker = Celery(__name__,
                include=["tasks"])
worker.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
worker.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


if __name__ == "__main__":
    worker.start()
