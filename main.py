from pathlib import Path
from contextlib import asynccontextmanager
import uvicorn
import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import FileResponse,  HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database.db import get_db
from src.routes import  auth, users, posts, transformations, tags, comments, rating
from src.conf.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):   
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
    yield

app = FastAPI(lifespan=lifespan)
# app = FastAPI()   # варіант з гілки dev

app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(posts.router, prefix='/api')
app.include_router(transformations.router, prefix='/api')
app.include_router(tags.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(rating.router, prefix='/api')

# варіант з гілки  dev
# @app.on_event('startup')
# async def startup():
#     r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
#     await FastAPILimiter.init(r)

# варіант з гілки  dev
# @app.get('/')
# def read_root():
#     return {'message': 'FastAPI'}


# варіант read_root без завантаження index.htlm
@app.get("/", description='Main page')
def read_root():
    return {"message": "Welcome to the FAST API from team #6"}  # ! відповідь перевіряється у тесті test_route_main.py


# варіант завантаження index.htlm: з FileResponse

@app.get("/sphinx", include_in_schema=False)  # endpoint '/sphinx' для документації 
async def get_docs():
    return FileResponse(Path("./docs/_build/html/index.html"), media_type="text/html")
# шлях Path("./docs/_build/html/index.html" працює, якщо сервер запускається з теки з файлом main.py

@app.get("/view-source", include_in_schema=False)   # endpoint '/view-source' викликається з документації
async def view_source():
    source_file_path = Path("./docs/_build/html/_sources/index.rst.txt")
    return FileResponse(source_file_path)


# варіант завантаження index.htlm: з Jinja2Templates (як пропозиція, часу перевіріти не було)

@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    templates = Jinja2Templates(directory="./docs/_build/html/index.html")
    return templates.TemplateResponse('index.html', {"request": request, "title": "Sphinx docs"})

@app.get("/indexsrc", response_class=HTMLResponse)
async def index(request: Request):
    templates = Jinja2Templates(directory="./docs/_build/html/_sources/index.rst.txt")  # чи загрузить корректно ?, чи FileResponse
    return templates.TemplateResponse('index.html', {"request": request, "title": "Sphinx docs"})



@app.get("/healthchecker", include_in_schema=False) # Database connection check
def healthchecker(db: Session = Depends(get_db)):
    try:    
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Database connection OK"}    # ! відповідь перевіряється у тесті test_route_main.py
    except Exception:
        raise HTTPException(status_code=500, detail="Error connecting to the database") 
    

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
