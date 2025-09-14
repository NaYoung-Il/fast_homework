import enum
from typing import Optional
from sqlalchemy import Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.database import Base

# 1. 역할(Role)을 위한 Enum 정의
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


# User 모델: 사용자 정보
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(100))
    # 2. role 컬럼 추가 (Enum 사용, 기본값은 USER)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER)

    refresh_token: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # User - Playlist 관계 설정 = 1:N 관계
    playlists: Mapped[list["Playlist"]] = relationship("Playlist", back_populates="user")


# Song 모델: 노래 정보
class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), index=True)
    artist: Mapped[str] = mapped_column(String(100))
    duration: Mapped[int] = mapped_column(Integer)  # duration in seconds

    playlists: Mapped[list["Playlist"]] = relationship(
        "Playlist", secondary="playlist_songs", back_populates="songs"
    )

# Playlist 모델: 플레이리스트 정보
class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    desc: Mapped[str] = mapped_column(String(200), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship("User", back_populates="playlists")
    songs: Mapped[list["Song"]] = relationship(
        "Song", secondary="playlist_songs", back_populates="playlists"
    )

# PlaylistSong 모델: 플레이리스트와 노래의 N:M 관계 테이블
class PlaylistSong(Base):
    __tablename__ = "playlist_songs" # 명시적 테이블 이름 지정
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id"), primary_key=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"), primary_key=True)