import os
import json
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
import classes

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


with open("utils/resources/fake_users_db.json", "r") as file:
    fake_users_db = json.load(file)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    This function verifies the password compared to the hashed password.

    Args:
        plain_password (str): the password to be verified
        hashed_password (str): the hashed password to be compared

    Returns:
        bool: True if the password is verified, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    This function hashes the password.

    Args:
        password (str): the password to be hashed

    Returns:
        str: the hashed password
    """
    return pwd_context.hash(password)


def get_user(db: dict, username: str) -> classes.UserInDB | None:
    """
    This function gets the user from the database.

    Args:
        db (dict): the database
        username (str): the username to be retrieved

    Returns:
        classes.UserInDB: the user retrieved from the database
    """
    if username in db:
        user_dict = db[username]
        return classes.UserInDB(**user_dict)


def authenticate_user(
    fake_db: dict, username: str, password: str
) -> classes.UserInDB | bool:
    """
    This function authenticates the user.

    Args:
        fake_db (dict): the database
        username (str): the username to be authenticated
        password (str): the password to be authenticated

    Returns:
        classes.UserInDB | bool: the user if authenticated, False otherwise
    """
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """
    This function creates an access token.

    Args:
        data (dict): the data to be encoded
        expires_delta (timedelta | None, optional): the expiration
            delta. Defaults to None.

    Returns:
        str: the encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def verify_generated_token(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> bool:
    """
    This function verifies the generated token.

    Args:
        authentication (classes.Authentication): the authentication
            token

    Returns:
        bool: True if the token is verified, False otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        expired = datetime.fromtimestamp(payload.get("exp")) < datetime.now()
        if username is None:
            return False
        return get_user(fake_users_db, username=username) and not expired
    except InvalidTokenError:
        return False
