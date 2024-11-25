from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from datetime import datetime, timedelta, timezone
from jose import jwt, ExpiredSignatureError, JWTError

from models.user import User
from backend.dp_depens import get_db

from schemas.schemas import CreateUser
from passlib.context import CryptContext

SECRET_KEY = "35c91ff427d70ae2b86823192c9cdfdf237b0cdd0a7ad0340ae26c4ececf15a9"
ALGHORITM = "HS256"

router = APIRouter(prefix="/auth", tags=["авторизация"])
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGHORITM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        is_admin: str = payload.get('is_admin')
        is_supplier: str = payload.get('is_supplier')
        is_customer: str = payload.get('is_customer')
        expire = payload.get('exp')
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )
        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token supplied"
            )
        return {
            'username': username,
            'id': user_id,
            'is_admin': is_admin,
            'is_supplier': is_supplier,
            'is_customer': is_customer,
        }
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired!"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )

async def get_username(db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str):
    user = await db.scalar(select(User).where(User.username == username))
    if not user or not bcrypt_context.verify(password, user.hashed_password) or user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Доступ запрещен",
            headers={"WWW-Autheniicate": "Bearer"},
        )
    return user

async def create_access_token(username: str,
                              user_id: int,
                              is_admin: bool,
                              is_supplier: bool,
                              is_customer: bool,
                              expirse_data: timedelta):
    encoded = {'sub': username, "id": user_id, 'is_admin': is_admin, 'is_supplier': is_supplier, 'is_customer': is_customer}
    expires = datetime.now(timezone.utc) + expirse_data
    encoded.update({"exp": expires})
    return jwt.encode(encoded, SECRET_KEY, algorithm=ALGHORITM)

@router.get("/read_current_user")
async def read_current_user(user: User = Depends(get_current_user)):
    return user


@router.post('/token')
async def login(db: Annotated[AsyncSession, Depends(get_db)], form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await get_username(db, form_data.username, form_data.password)
    token = await create_access_token(user.username, user.id, user.is_admin, user.is_supplier, user.is_customer, timedelta(minutes=20))

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser):
    await db.execute(insert(User).values(first_name=create_user.first_name,
                                         last_name=create_user.last_name,
                                         username=create_user.username,
                                         email=create_user.email,
                                         hashed_password=bcrypt_context.hash(create_user.password),
                                         ))
    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

