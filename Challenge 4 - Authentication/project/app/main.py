from fastapi import FastAPI

from app.database import engine, Base
from app import models

from app.routers.auth_router import router as auth_router
from app.routers.product_router import router as product_router
from app.routers.profile_router import router as profile_router
from app.routers.dashboard_router import router as dashboard_router

app = FastAPI(
    title="Production FastAPI App"
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(profile_router)
app.include_router(dashboard_router)