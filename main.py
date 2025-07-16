from fastapi import FastAPI
from contextlib import asynccontextmanager
from tasks.routes import accounts_router, tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("application startup")
    yield
    print("application shutdown")


app = FastAPI(Lifespan=lifespan)

app.include_router(accounts_router)
app.include_router(tasks_router)

