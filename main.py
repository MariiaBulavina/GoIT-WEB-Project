import os

from fastapi import FastAPI
import uvicorn
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis

from src.routes import  auth, users, posts, transformations, tags, comments, rating
from src.conf.config import settings


app = FastAPI()

app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(posts.router, prefix='/api')
app.include_router(transformations.router, prefix='/api')
app.include_router(tags.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(rating.router, prefix='/api')

@app.on_event('startup')
async def startup():
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, password=settings.redis_password)
    await FastAPILimiter.init(r)


@app.get('/')
def read_root():
    return {'message': 'FastAPI'}


