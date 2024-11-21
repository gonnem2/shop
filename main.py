from fastapi import FastAPI, status

from routers.category import router as category
from routers.products import router as product
from routers.auth import router as auth


app = FastAPI(version="0.0.1", title="My App")

app.include_router(category)
app.include_router(product)
app.include_router(auth)