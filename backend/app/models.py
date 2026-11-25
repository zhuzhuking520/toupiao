# -*- coding: utf-8 -*-
"""数据模型：核心 4 张表（用户/投票/选项/投票记录）

设计要点：
- vote_record 对 (vote_id, user_id, option_id) 建唯一约束，
  配合接口层的「该用户是否已投过此投票」检查，双重防止重复投票。
- 多选题：同一用户对同一投票的多条选项记录 = 一次提交。
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    votes = relationship("Vote", back_populates="creator")


class Vote(Base):
    __tablename__ = "vote"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, default="")
    # single = 单选，multiple = 多选
    vote_type: Mapped[str] = mapped_column(String(10), default="single")
    # 多选题最多可选项数（单选题恒为 1）
    max_choices: Mapped[int] = mapped_column(Integer, default=1)
    # 是否匿名：匿名则结果页不展示投票人
    anonymous: Mapped[bool] = mapped_column(Boolean, default=True)
    # open = 进行中, closed = 已关闭
    status: Mapped[str] = mapped_column(String(10), default="open")
    deadline: Mapped[datetime] = mapped_column(DateTime)
    creator_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    creator = relationship("User", back_populates="votes")
    options = relationship(
        "VoteOption", back_populates="vote", order_by="VoteOption.sort"
    )


class VoteOption(Base):
    __tablename__ = "vote_option"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vote_id: Mapped[int] = mapped_column(ForeignKey("vote.id"), index=True)
    content: Mapped[str] = mapped_column(String(200))
    sort: Mapped[int] = mapped_column(Integer, default=0)

    vote = relationship("Vote", back_populates="options")
    records = relationship("VoteRecord", back_populates="option")


class VoteRecord(Base):
    __tablename__ = "vote_record"
    __table_args__ = (
        UniqueConstraint("vote_id", "user_id", "option_id", name="uq_vote_user_option"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vote_id: Mapped[int] = mapped_column(ForeignKey("vote.id"), index=True)
    option_id: Mapped[int] = mapped_column(ForeignKey("vote_option.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)
    voted_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    option = relationship("VoteOption", back_populates="records")
