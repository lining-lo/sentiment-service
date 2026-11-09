from fastapi import FastAPI

from sentiment.app.routers.rest.system_router import router

app = FastAPI(description="舆情分析")

# 挂载路由
app.include_router(router)