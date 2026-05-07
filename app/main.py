from fastapi import FastAPI
from api.verify import router as verify_router

app = FastAPI()
app.include_router(verify_router)