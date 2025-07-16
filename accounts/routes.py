from fastapi import APIRouter

# accounts_router = APIRouter()

@accounts_router.get("/accounts")
async def get_accounts():
    return {"message": "Hello World"}