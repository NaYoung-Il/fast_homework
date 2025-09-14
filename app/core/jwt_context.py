from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from app.core.settings import settings
import uuid

pwd_context = CryptContext(schemes=["bcrypt"])

# 해시값 저장
async def get_pwd_hash(password:str):
    return pwd_context.hash(password)

# 비밀번호 검증
async def verify_pwd(plain_password:str, hashed_password:str):
    return pwd_context.verify(plain_password, hashed_password)

# JWT 토큰 생성
def create_token(uid: int, expires_delta: timedelta, **kwargs) -> str:
    to_encode = kwargs.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "uid": uid})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.jwt_algo
    )
    return encoded_jwt

def create_access_token(uid: int) -> str:
    return create_token(
        uid=uid, expires_delta=settings.access_token
    )

def create_refresh_token(uid: int) -> str:
    return create_token(
        uid=uid, jti=str(uuid.uuid4()), expires_delta=settings.refresh_token
    )

def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algo],
    )

# 요청에 포함된 토큰의 유효성을 검증, 사용자 ID(uid)를 추출
def verify_token(token: str) -> int:
    payload = decode_token(token)
    return payload.get("uid")