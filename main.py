from typing import Generator, Optional
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import cv2
from yolomodel.yolov8 import inference as yolo_inference
from arduino.motor import motor
import models
from models import Batches
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import engine, sessionlocal
from datetime import datetime

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")    
templates = Jinja2Templates(directory="templates")

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

camera = cv2.VideoCapture(0)
inferencing = False

def gen_frames() -> Generator[bytes, None, None]:
    global inferencing, camera
    while True:
        success, frame = camera.read()
        if success:
            if inferencing:
                fruit, probs = yolo_inference(frame)
                motor(fruit, probs)
            try:
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            except Exception as e:
                print("Error encoding frame:", e)

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get('/video_feed')
async def video_feed():
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.post('/inference')
async def inference(request: Request, inference: bool = Form(...)):
    global inferencing
    if inference:
        inferencing = True
    else:
        inferencing = False
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("home.html", {"request": request, "inferencing": inferencing})

@app.post('/select_fruit')
async def select_fruit(request: Request, fruit: str = Form(...)):
    # Storing or Process fruit information
    return RedirectResponse(url="/", status_code=303)

@app.get('/track-record')
async def home(request: Request, db: Session = Depends(get_db)):
    batches = db.query(models.Batches).order_by(models.Batches.id.desc())
    return templates.TemplateResponse("history.html", {"request": request, "batches": batches})

def search_batch(query: str, db: Session):  
    batches = db.query(Batches).filter(Batches.date.contains(query))
    return batches

@app.get("/search")
async def search(request: Request, db: Session = Depends(get_db), query: Optional[str] = None):
    try:
        batches = search_batch(query, db=db)
        return templates.TemplateResponse("history.html", {"request": request, "batches": batches})
    except Exception as e:
        return RedirectResponse(url="/track-record", status_code=303)
    
@app.get("/autocomplete")
def autocomplete(term: Optional[str] = None, db: Session = Depends(get_db)):
    batches = search_batch(term, db=db)
    batches_date = set()
    for batch in batches:
        batches_date.add(batch.date)
    return list(batches_date)

def create_test_data(db: Session):
    db.add(Batches(batch_num=1, fruit='Apple', date='02/06/2022'))
    db.add(Batches(batch_num=2, fruit='Banana', date='02/07/2022'))
    db.add(Batches(batch_num=3, fruit='Orange', date='02/08/2022'))
    db.add(Batches(batch_num=3, fruit='Lemon', date='02/08/2022'))
    db.commit()

def delete_test_data(db: Session):
    test_batches = db.query(Batches).filter(Batches.fruit.in_(['Apple', 'Banana', 'Orange'])).all()
    for batch in test_batches:
        db.delete(batch)
    db.commit()

# //Get the current date and time
# current_date_time = datetime.now()

# //Extract only the date portion and convert it to a string with the format 'MM/DD/YYYY'
# date_string = current_date_time.strftime('%m/%d/%Y')

# print("Current date:", date_string)


