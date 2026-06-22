"""API v1 router aggregation."""

from fastapi import APIRouter
from app.api.v1 import auth, businesses, debtors, credits, analytics, webhooks

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["Businesses"])
api_router.include_router(debtors.router, prefix="/debtors", tags=["Debtors"])
api_router.include_router(credits.router, prefix="/credits", tags=["Credits"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
