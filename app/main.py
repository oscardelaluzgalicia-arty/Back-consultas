from fastapi import FastAPI
from api.verify import router as verify_router
from api.tables import router as tables_router
from api.describe import router as describe_router
from api.query import router as query_router

app = FastAPI()
app.include_router(verify_router)
app.include_router(tables_router)
app.include_router(describe_router)
app.include_router(query_router)
