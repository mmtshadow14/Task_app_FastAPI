# fastapi models
from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Response
from typing import List
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

# app models
from tasks.schemas import *
from tasks.models import TaskModel, UserModel, OtpcodeModel
from core.database import get_db
from auth.jwt import create_access_token, retrieve_user_via_jwt

# utils
from utils import generate_hash_password, verify_password, generate_otpcode

# APIRoute
accounts_router = APIRouter(prefix="/accounts", tags=["Accounts"])
tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


# register a new user
@accounts_router.post('/register', status_code=status.HTTP_201_CREATED, response_model=UserRegisterSchema)
async def register_user(request: UserRegisterSchema, response: Response, db: Session = Depends(get_db)):
    """
    with this route we will create a new user and set and itp code for the user to activate his account and will store
    his account id in his cookie to get it in the activate_user route to understand which account wants to be activated
    """
    is_username_exists = db.query(UserModel).filter_by(username=request.username).one_or_none()
    if is_username_exists:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='invalid username')
    hashed_password = generate_hash_password(request.password)
    new_user = UserModel(username=request.username, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    otp = generate_otpcode(new_user.id, response)
    db.add(otp)
    db.commit()
    return new_user


# activate a registered account
@accounts_router.post('/activate', )
async def activate_user(request: UserActivateSchema, user_id: int = Cookie(None), db: Session = Depends(get_db)):
    """
    with this route the user can activate his account, and we will do it with the id that comes from the Cookie that
     we saved it in the register_user route
    """
    otp_obj = db.query(OtpcodeModel).filter_by(user_id=user_id).one_or_none()
    if otp_obj and otp_obj.code == request.code:
        user = db.query(UserModel).filter_by(id=user_id).one_or_none()
        user.is_active = True
        db.commit()
        db.refresh(user)
        return JSONResponse({'message': f'{user.username} has been activated successfully'})
    raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='invalid information')


# get jwt token
@accounts_router.post('/get_token', status_code=status.HTTP_201_CREATED)
async def get_token(request: GetTokenSchema, db: Session = Depends(get_db)):
    """
    with this route the user can get a JWT access token if his account be active with sending his username and password
    """
    user = db.query(UserModel).filter_by(username=request.username).one_or_none()
    if user and verify_password(request.password, user.password):
        if user.is_active:
            jwt_token = create_access_token(user.id)
            return {'token': jwt_token}
        return HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail='this user is not active')
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail='we couldn\'t verify you with provided information')


# get all tasks
@tasks_router.post('/retrieve_all_tasks', status_code=status.HTTP_200_OK, response_model=List[TaskResponseSchema])
async def get_all_tasks(request: RetrieveTaskSchema, db: Session = Depends(get_db)):
    """
    with this route if the user has a JWT token, he can retrieve all tasks that are related to him
    """
    if request.token:
        user = retrieve_user_via_jwt(request.token)
        if user:
            tasks = db.query(TaskModel).filter_by(user_id=user.id).all()
            return tasks
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='we couldn\'t verify you with provided '
                                                                             'information')
    raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail='we couldn\'t verify you with provided'
                                                                                ' information')


# get a task with ID
@tasks_router.post('/retrieve_task/{task_id}', status_code=status.HTTP_200_OK, response_model=TaskResponseSchema)
async def get_task_with_id(task_id: int, request: RetrieveTaskSchema, db: Session = Depends(get_db)):
    """
    with this route if the user has a JWT token, he can retrieve one of the tasks that are related to him
    """
    if request.token:
        user = retrieve_user_via_jwt(request.token)
        task = db.query(TaskModel).filter_by(id=task_id).one_or_none()
        if user:
            if task:
                if task.user_id == user.id:
                    return task
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='you don\'t own this task')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='we couldn\'t find the task')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='we couldn\'t verify you with provided '
                                                                             'information')
    raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail='we couldn\'t verify you with provided'
                                                                                ' information')


# create tasks
@tasks_router.post('/create_task', status_code=status.HTTP_201_CREATED, response_model=TaskResponseSchema)
async def create_tasks(request: CreateTaskSchema, db: Session = Depends(get_db)):
    """
    with this route if the user has a JWT token, he can create a task.
    """
    if request.token:
        user = retrieve_user_via_jwt(request.token)
        if not request.title:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='title is required')
        new_task = TaskModel(user_id=user.id, title=request.title)
        if request.description:
            new_task.description = request.description
            db.add(new_task)
            db.commit()
            db.refresh(new_task)
            return new_task
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail='we couldn\'t verify you with provided'
                                                                                ' information')


# update tasks
@tasks_router.post('/update_task/{post_id}', status_code=status.HTTP_202_ACCEPTED, response_model=TaskResponseSchema)
async def update_tasks(request: CreateTaskSchema, task_id: int, db: Session = Depends(get_db)):
    """
    with this route if the user has a JWT token, he can update the tasks he owns.
    """
    if request.token:
        user = retrieve_user_via_jwt(request.token)
        task = db.query(TaskModel).filter_by(id=task_id).one_or_none()
        if task:
            if task.user_id == user.id:
                if request.title:
                    task.title = request.title
                if request.description:
                    task.description = request.description
                db.commit()
                return task
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='you cant update this task')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='we couldn\'t find the task')
    raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail='we couldn\'t verify you with provided'
                                                                                ' information')


# set tasks done
@tasks_router.post('/set_task_done/{post_id}', status_code=status.HTTP_200_OK, response_model=TaskResponseSchema)
async def set_done_tasks(request: RetrieveTaskSchema, task_id: int, db: Session = Depends(get_db)):
    """
    with this route if the user has a JWT token, he can change the tasks done status of his own.
    """
    if request.token:
        user = retrieve_user_via_jwt(request.token)
        task = db.query(TaskModel).filter_by(id=task_id).one_or_none()
        if task:
            if task.user_id == user.id:
                task.done = True
                db.commit()
                db.refresh(task)
                return JSONResponse({'message': f'we changed the status of the {task.id} task to done.'})
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='you cant update this task')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='we couldn\'t find the task')
    raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail='we couldn\'t verify you with provided'
                                                                                ' information')


# set tasks done
@tasks_router.post('/delete_task/{post_id}',)
async def delete_tasks(request: RetrieveTaskSchema, task_id: int, db: Session = Depends(get_db)):
    """
    with this route if the user has a JWT token, he can delete the tasks of his own.
    """
    if request.token:
        user = retrieve_user_via_jwt(request.token)
        task = db.query(TaskModel).filter_by(id=task_id).one_or_none()
        if task:
            if task.user_id == user.id:
                db.delete(task)
                db.commit()
                return HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail=f'we deleted the {task_id} successfully.')
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='you cant delete this task')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='we couldn\'t find the task')
    raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail='we couldn\'t verify you with provided'
                                                                                ' information')















