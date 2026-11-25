# -*- coding: utf-8 -*-
"""投票接口：列表 / 创建 / 详情 / 提交 / 结果 / 关闭

当前骨架先实现 auth 验证 + 列表与创建，其余接口在任务 3/4 补全。
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from .auth import get_current_user
from .db import get_db
from .models import User, Vote, VoteOption, VoteRecord

router = APIRouter(prefix="/api/votes", tags=["votes"])
CST = ZoneInfo("Asia/Shanghai")


class OptionIn(BaseModel):
    content: str = Field(min_length=1, max_length=200)


class VoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=2000)
    vote_type: str = Field(pattern="^(single|multiple)$")
    max_choices: int = Field(default=1, ge=1, le=20)
    anonymous: bool = True
    deadline: str  # ISO 格式，如 2026-12-31T23:59:59
    options: list[OptionIn] = Field(min_length=2, max_length=20)


def vote_open(vote: Vote) -> bool:
    """投票是否可投：状态开放且未过截止时间（含自动截止判定）"""
    if vote.status != "open":
        return False
    deadline = vote.deadline.replace(tzinfo=CST)
    return datetime.now(CST) <= deadline


@router.get("", name="投票列表")
def list_votes(
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = (
        select(Vote)
        .options(joinedload(Vote.options))
        .order_by(Vote.created_at.desc())
    )
    votes = db.scalars(query).unique().all()
    result = []
    for v in votes:
        # 读取时惰性执行自动截止：过线即关
        if v.status == "open" and not vote_open(v):
            v.status = "closed"
        open_now = v.status == "open"
        if status_filter == "open" and not open_now:
            continue
        if status_filter == "closed" and open_now:
            continue
        result.append(
            {
                "id": v.id,
                "title": v.title,
                "description": v.description,
                "vote_type": v.vote_type,
                "status": v.status,
                "deadline": v.deadline.isoformat(),
                "anonymous": v.anonymous,
                "creator": v.creator.username,
                "option_count": len(v.options),
            }
        )
    return result


@router.post("", status_code=201, name="创建投票")
def create_vote(
    data: VoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    max_choices = 1 if data.vote_type == "single" else data.max_choices
    try:
        deadline = datetime.fromisoformat(data.deadline)
    except ValueError:
        raise HTTPException(status_code=422, detail="截止时间格式错误")
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=CST)
    if datetime.now(CST) >= deadline:
        raise HTTPException(status_code=422, detail="截止时间必须晚于当前时间")

    vote = Vote(
        title=data.title,
        description=data.description,
        vote_type=data.vote_type,
        max_choices=max_choices,
        anonymous=data.anonymous,
        deadline=deadline,
        creator_id=user.id,
    )
    db.add(vote)
    db.flush()
    for i, opt in enumerate(data.options):
        db.add(VoteOption(vote_id=vote.id, content=opt.content, sort=i))
    db.commit()
    db.refresh(vote)
    return {"id": vote.id, "title": vote.title}


@router.patch("/{vote_id}/close", name="提前关闭投票")
def close_vote(
    vote_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vote = db.get(Vote, vote_id)
    if vote is None:
        raise HTTPException(status_code=404, detail="投票不存在")
    if vote.creator_id != user.id:
        raise HTTPException(status_code=403, detail="只有发起人才能关闭投票")
    if vote.status == "closed":
        raise HTTPException(status_code=422, detail="投票已经关闭，无需重复操作")
    vote.status = "closed"
    db.commit()
    return {"id": vote.id, "status": vote.status}


@router.delete("/{vote_id}", name="删除投票")
def delete_vote(
    vote_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vote = db.get(Vote, vote_id)
    if vote is None:
        raise HTTPException(status_code=404, detail="投票不存在")
    if vote.creator_id != user.id:
        raise HTTPException(status_code=403, detail="只有发起人才能删除投票")
    # 先删投票记录和选项，再删投票本体（SQLite 无级联配置，手动保证一致性）
    option_ids = db.scalars(
        select(VoteOption.id).where(VoteOption.vote_id == vote_id)
    ).all()
    db.query(VoteRecord).filter(VoteRecord.option_id.in_(option_ids)).delete(
        synchronize_session=False
    )
    db.query(VoteOption).filter(VoteOption.vote_id == vote_id).delete(
        synchronize_session=False
    )
    db.delete(vote)
    db.commit()
    return {"deleted": vote_id}


@router.get("/mine/list", name="我的投票")
def my_votes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    votes = (
        db.scalars(
            select(Vote)
            .options(joinedload(Vote.options))
            .where(Vote.creator_id == user.id)
            .order_by(Vote.created_at.desc())
        )
        .unique()
        .all()
    )
    result = []
    for v in votes:
        if v.status == "open" and not vote_open(v):
            v.status = "closed"
        record_count = (
            db.query(VoteRecord)
            .filter(
                VoteRecord.vote_id == v.id,
            )
            .distinct(VoteRecord.user_id)
            .count()
        )
        result.append(
            {
                "id": v.id,
                "title": v.title,
                "vote_type": v.vote_type,
                "status": v.status,
                "deadline": v.deadline.isoformat(),
                "anonymous": v.anonymous,
                "option_count": len(v.options),
                "voter_count": record_count,
            }
        )
    return result


class BallotIn(BaseModel):
    option_ids: list[int] = Field(min_length=1, max_length=20)


@router.post("/{vote_id}/ballot", status_code=201, name="提交投票")
def submit_ballot(
    vote_id: int,
    data: BallotIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vote = db.get(Vote, vote_id)
    if vote is None:
        raise HTTPException(status_code=404, detail="投票不存在")
    if not vote_open(vote):
        raise HTTPException(status_code=422, detail="投票已截止或已关闭，无法参与")

    already = db.scalar(
        select(VoteRecord.id).where(
            VoteRecord.vote_id == vote_id, VoteRecord.user_id == user.id
        )
    )
    if already is not None:
        raise HTTPException(status_code=409, detail="您已参与过此投票，请勿重复提交")

    # 校验选项：必须属于该投票，且去重
    requested = list(dict.fromkeys(data.option_ids))  # 去重保序
    valid_ids = set(
        db.scalars(select(VoteOption.id).where(VoteOption.vote_id == vote_id)).all()
    )
    invalid = [oid for oid in requested if oid not in valid_ids]
    if invalid:
        raise HTTPException(status_code=422, detail="包含无效选项")
    limit = 1 if vote.vote_type == "single" else vote.max_choices
    if len(requested) > limit:
        raise HTTPException(
            status_code=422,
            detail=f"最多可选 {limit} 项，当前选择了 {len(requested)} 项",
        )

    for oid in requested:
        db.add(VoteRecord(vote_id=vote_id, option_id=oid, user_id=user.id))
    db.commit()
    return {"voted": True, "options": requested}


@router.get("/{vote_id}/result", name="查看结果")
def vote_result(
    vote_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vote = db.get(Vote, vote_id)
    if vote is None:
        raise HTTPException(status_code=404, detail="投票不存在")
    options = db.scalars(
        select(VoteOption).where(VoteOption.vote_id == vote_id).order_by(VoteOption.sort)
    ).all()
    records = db.scalars(select(VoteRecord).where(VoteRecord.vote_id == vote_id)).all()
    voter_ids = {r.user_id for r in records}
    total_voters = len(voter_ids)

    # 非匿名投票时收集「选项 -> 投票人名单」
    users_by_option: dict[int, list[str]] = {}
    if not vote.anonymous and records:
        user_map = {
            u.id: u.username
            for u in db.scalars(
                select(User).where(User.id.in_(voter_ids))
            ).all()
        }
        for r in records:
            users_by_option.setdefault(r.option_id, []).append(
                user_map.get(r.user_id, "未知用户")
            )

    result = []
    for o in options:
        count = sum(1 for r in records if r.option_id == o.id)
        result.append(
            {
                "option_id": o.id,
                "content": o.content,
                "count": count,
                "percent": round(count / total_voters * 100, 1) if total_voters else 0.0,
                "voters": users_by_option.get(o.id, []),
            }
        )
    return {
        "vote_id": vote.id,
        "title": vote.title,
        "status": vote.status,
        "anonymous": vote.anonymous,
        "total_voters": total_voters,
        "options": result,
    }


@router.get("/{vote_id}", name="投票详情")
def vote_detail(
    vote_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vote = db.get(Vote, vote_id)
    if vote is None:
        raise HTTPException(status_code=404, detail="投票不存在")
    if vote.status == "open" and not vote_open(vote):
        vote.status = "closed"
        db.commit()
    voted = db.scalar(
        select(VoteRecord.id).where(
            VoteRecord.vote_id == vote_id, VoteRecord.user_id == user.id
        )
    )
    return {
        "id": vote.id,
        "title": vote.title,
        "description": vote.description,
        "vote_type": vote.vote_type,
        "max_choices": vote.max_choices,
        "anonymous": vote.anonymous,
        "status": vote.status,
        "deadline": vote.deadline.isoformat(),
        "creator": vote.creator.username,
        "options": [
            {"id": o.id, "content": o.content, "sort": o.sort} for o in vote.options
        ],
        "voted": voted is not None,
    }
