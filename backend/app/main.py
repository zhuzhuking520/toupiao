# -*- coding: utf-8 -*-
"""WebVote 后端入口：FastAPI 应用"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401 确保模型注册
from .auth import router as auth_router
from .db import engine
from .votes import router as votes_router

# 启动时建表（课程项目够用；生产应使用迁移工具）
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="WebVote 在线投票系统", version="0.1.0")

# 前后端分离：允许 Vite 开发服务器跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(votes_router)


@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok"}
