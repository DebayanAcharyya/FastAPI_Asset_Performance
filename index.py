from fastapi import FastAPI
from routes.asset import asset
from routes.performance import performance
from routes.aggregation import aggregation
from routes.auth import auth
from config.db import Database, close_database_client


app = FastAPI()
app.include_router(asset)
app.include_router(performance)
app.include_router(aggregation)
app.include_router(auth)

# Dependency to ensure the database is initialized
async def ensure_database_initialized():
    Database()

@app.on_event("startup")
async def startup_event():
    await ensure_database_initialized()

@app.on_event("shutdown")
async def shutdown_event():
    await close_database_client()


