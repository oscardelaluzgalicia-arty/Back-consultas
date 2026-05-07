from fastapi import FastAPI
from api.verify import router as verify_router
from api.tables import router as tables_router

app = FastAPI()
app.include_router(verify_router)
app.include_router(tables_router)