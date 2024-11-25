from fastapi import FastAPI, status

from routers.category import router as category
from routers.products import router as product
from routers.auth import router as auth
from routers.permissions import router as permission
from routers.reviews import router as review


app = FastAPI(version="0.0.1", title="My App")

app.include_router(category)
app.include_router(product)
app.include_router(auth)
app.include_router(permission)
app.include_router(review)