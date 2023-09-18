from fastapi import FastAPI
from app.db.config import config_database

app = FastAPI()

if __name__ == "__main__":
    config_database()
