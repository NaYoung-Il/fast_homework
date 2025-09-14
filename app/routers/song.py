from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.schemas.schemas import SongRead, SongCreate, SongUpdate, UserRead
from app.services import services
from app.db.database import get_db
from app.core.auth import get_admin_user

router = APIRouter(prefix="/songs", tags=["Song"])

# 노래 생성 (관리자만 가능)
@router.post("/", response_model=SongRead, status_code=status.HTTP_201_CREATED)
async def create_song(
    song: SongCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: UserRead = Depends(get_admin_user) # 관리자 권한 확인
):
    return await services.SongService.create_song(db, song)

# 모든 노래 목록 조회 (모든 사용자 가능)
@router.get("/", response_model=List[SongRead])
async def get_all_songs(db: AsyncSession = Depends(get_db)):
    return await services.SongService.get_all_songs(db)

# 특정 노래 조회 (모든 사용자 가능)
@router.get("/{song_id}", response_model=SongRead)
async def get_song(song_id: int, db: AsyncSession = Depends(get_db)):
    return await services.SongService.get_song(db, song_id)

# 노래 정보 수정 (관리자만 가능)
@router.patch("/{song_id}", response_model=SongRead)
async def update_song(
    song_id: int,
    song_update: SongUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: UserRead = Depends(get_admin_user) # 관리자 권한 확인
):
    return await services.SongService.update_song(db, song_id, song_update)

# 노래 삭제 (관리자만 가능)
@router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_song(
    song_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: UserRead = Depends(get_admin_user) # 관리자 권한 확인
):
    await services.SongService.delete_song(db, song_id)
    return {"detail": "노래가 성공적으로 삭제되었습니다."}