# WebVote 在线投票系统

软件工程期末大作业：前后端分离的在线投票系统，支持发起投票、分享链接、参与投票、结果统计。

## 技术栈

- 前端：Vue 3 + Vite + Element Plus + ECharts
- 后端：Python FastAPI + SQLAlchemy + JWT
- 数据库：SQLite（开发环境，可平滑迁移 MySQL）

## 功能

- 用户注册 / 登录（JWT 认证，PBKDF2 密码加密）
- 发起投票：单选/多选、匿名/实名、截止时间、动态选项
- 投票大厅：浏览全部投票，点击进入详情
- 参与投票：防重复提交（数据库唯一约束 + 接口校验双层防护）
- 结果统计：票数 / 占比图表（ECharts），实名投票展示投票人名单
- 投票管理：发起人可提前关闭、删除自己的投票
- 自动截止：超过截止时间自动关闭，不可再投

## 项目结构

```
webvote/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── main.py       # 应用入口（CORS、路由注册）
│   │   ├── db.py         # 数据库连接与会话
│   │   ├── models.py     # ORM 模型（4 张核心表）
│   │   ├── security.py   # 密码哈希 + JWT
│   │   ├── auth.py       # 注册/登录接口
│   │   └── votes.py      # 投票接口
│   └── run.py           # 启动脚本
└── frontend/         # Vue 3 前端
    └── src/
        ├── api/http.js      # axios 封装（自动携带 JWT）
        ├── router/          # 路由与登录守卫
        └── views/           # 登录/注册/大厅/详情/发起/我的投票
```

## 本地运行

后端（需 Python 3.10+，先 `pip install fastapi uvicorn sqlalchemy pyjwt tzdata`）：

```bash
cd backend
python run.py        # 运行在 http://127.0.0.1:8000，自动建表
```

前端（需 Node 18+）：

```bash
cd frontend
npm install
npm run dev          # 运行在 http://localhost:5173
```

接口文档（FastAPI 自动生成）：http://127.0.0.1:8000/docs

## 测试账号

| 用户名 | 密码 |
|---|---|
| testuser | abc12345 |
| voter2 | xyz65432 |
