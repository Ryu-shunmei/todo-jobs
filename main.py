from uvicorn import run
from fastapi import FastAPI
from api import users_router

app = FastAPI(title='FastAPI 入门教程', version='0.0.1')

app.include_router(users_router)

if __name__ == '__main__':
    run(app='main:app', host="0.0.0.0", port=8000, reload=True)
