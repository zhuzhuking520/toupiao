# -*- coding: utf-8 -*-
"""数据库连接与会话管理（SQLite，后续可无缝切换 MySQL）"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./webvote.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # SQLite 需要，允许跨线程访问
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 依赖：每个请求一个数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
