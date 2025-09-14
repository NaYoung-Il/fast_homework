from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.schemas.schemas import PlaylistRead, PlaylistCreate, PlaylistUpdate
from app.services.services import PlaylistService, PlaylistSongService
from app.db.database import get_db
from app.db.models.models import User
from app.core.auth import get_current_user # 현재 로그인한 사용자 정보

router = APIRouter(prefix="/playlists", tags=["Playlist"])

# 플레이리스트 생성 (로그인한 사용자 본인)
@router.post("/", response_model=PlaylistRead, status_code=status.HTTP_201_CREATED)
async def create_playlist(
    playlist: PlaylistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await PlaylistService.create_playlist(db, playlist, current_user.id)

# 현재 유저의 모든 플레이리스트 목록 조회
@router.get("/", response_model=List[PlaylistRead])
async def get_my_playlists(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await PlaylistService.get_user_playlists(db, current_user.id)

# 특정 플레이리스트 조회 (본인만 가능)
@router.get("/{playlist_id}", response_model=PlaylistRead)
async def get_playlist(
    playlist_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_playlist = await PlaylistService.get_playlist(db, playlist_id)
    if db_playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="플레이리스트에 접근할 권한이 없습니다.")
    return db_playlist

# 플레이리스트 정보 수정 (본인만 가능)
@router.patch("/{playlist_id}", response_model=PlaylistRead)
async def update_playlist(
    playlist_id: int,
    playlist_update: PlaylistUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_playlist = await PlaylistService.get_playlist(db, playlist_id)
    if db_playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="플레이리스트를 수정할 권한이 없습니다.")
    return await PlaylistService.update_playlist(db, playlist_id, playlist_update)

# 플레이리스트 삭제 (본인만 가능)
@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_playlist(
    playlist_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_playlist = await PlaylistService.get_playlist(db, playlist_id)
    if db_playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="플레이리스트를 삭제할 권한이 없습니다.")
    await PlaylistService.delete_playlist(db, playlist_id)
    return {"detail": "플레이리스트가 성공적으로 삭제되었습니다."}

# 플레이리스트에 노래 추가
@router.post("/{playlist_id}/songs/{song_id}", response_model=PlaylistRead)
async def add_song_to_playlist(
    playlist_id: int,
    song_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_playlist = await PlaylistService.get_playlist(db, playlist_id)
    if db_playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="플레이리스트를 수정할 권한이 없습니다.")
    return await PlaylistSongService.add_song_to_playlist(db, playlist_id, song_id)

# 플레이리스트에 노래 제거
@router.delete("/{playlist_id}/songs/{song_id}", response_model=PlaylistRead)
async def remove_song_from_playlist(
    playlist_id: int,
    song_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_playlist = await PlaylistService.get_playlist(db, playlist_id)
    if db_playlist.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="플레이리스트를 수정할 권한이 없습니다.")
    return await PlaylistSongService.remove_song_from_playlist(db, playlist_id, song_id)