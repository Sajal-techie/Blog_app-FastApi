from fastapi import FastAPI, Depends,status, Response, HTTPException
import uvicorn
from sqlalchemy.orm import Session
from . import schema, models
from .database import engine, SessionLocal

app = FastAPI()

models.Base.metadata.create_all(bind=engine) 


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/blog', status_code=status.HTTP_201_CREATED)
def create(request: schema.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.get('/blog')
def get_all(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs


@app.get('/blog/{id}', status_code=status.HTTP_200_OK)
def get_one(id,response: Response, db: Session = Depends(get_db) ):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if blog:
        return blog
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"blog with {id} not available")


@app.delete('/blog/{id}',  status_code=status.HTTP_204_NO_CONTENT)
def delete(id, response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"blog with id:{id} not found")
    blog.delete(synchronize_session=False)
    db.commit()
    return {f'{blog} blog deleted successfully'}


@app.put('/blog/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id, request: schema.Blog, db: Session = Depends(get_db)):
    print(request)
    blog = db.query(models.Blog).filter(models.Blog.id==id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"no blog with id{id}")
    blog.update(request.model_dump())
    db.commit()
    return blog
