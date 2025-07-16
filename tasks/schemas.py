from pydantic import BaseModel, Field


class UserRegisterSchema(BaseModel):
    username: str = Field(...)
    password: str = Field(...)


class UserActivateSchema(BaseModel):
    code: int = Field(...)


class GetTokenSchema(BaseModel):
    username: str = Field(...)
    password: str = Field(...)


class TaskResponseSchema(BaseModel):
    id: int = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    done: bool = Field(...)


class RetrieveTaskSchema(BaseModel):
    token: str = Field(...)


class CreateTaskSchema(BaseModel):
    token: str = Field(...)
    title: str = Field(...)
    description: str = Field(...)
