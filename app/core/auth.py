from fastapi import Request, Response, HTTPException, Depends
from jwt import InvalidTokenError
from app.core.settings import settings
from app.core.jwt_context import verify_token
from app.db.database import get_db
from app.services.services import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.models import UserRole

def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=int(settings.access_token.total_seconds()),
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=int(settings.refresh_token.total_seconds()),
    )

# 요청객체에서 access_token 꺼내서 현재 로그인한 사용자 ID 반환
async def get_user_id(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Access token missing")
    
    try:
        user_id = verify_token(access_token)
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
# access_token이 없어도 예외 던지지 않고 None 반환
# 로그인 여부가 선택적인 API에서 사용 -> 로그인 안 해도 볼 수 있는 페이지
async def get_user_id_option(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return None
    
    try:
        return verify_token(access_token)
    except InvalidTokenError:
        return None
    
# 관리자만 접근 가능하도록 하는 의존성
async def get_admin_user(user_id: int = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    user = await UserService.get_user(db, user_id)
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다. 관리자만 접근 가능합니다.")
    return user

# 현재 로그인한 사용자 객체를 반환하는 의존성
async def get_current_user(user_id: int = Depends(get_user_id), db: AsyncSession = Depends(get_db)):
    return await UserService.get_user(db, user_id)