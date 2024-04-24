from typing import Generator, Optional
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import cv2
from yolomodel.yolov8 import FruitClassifier
import models
from models import Batches
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import engine, sessionlocal
from datetime import datetime
from collections import Counter
import serial
from arduino.arduino import servo

arduino = serial.Serial(port='COM3', baudrate=2000000, timeout=.1)

models.Base.metadata.create_all(bind=engine)

model_path = "D:\\webPrac\\fastapi\\yolomodel\\best1.pt"
fruit_classifier = FruitClassifier(model_path)

freshCount, rottenCount = 0,0
fruit_sequence = []

# Define your Region of Interest (ROI) coordinates
roi_x1, roi_y1 = 170, 0  # Top-left corner of the ROI
roi_x2, roi_y2 = 490, 480  # Bottom-right corner of the ROI

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
fruit_choice = None


def gen_frames() -> Generator[bytes, None, None]:
    global inferencing, camera
   
    while True:
        success, frame = camera.read()
        if success:
            if inferencing:
                roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]
                predicted_class, probs = fruit_classifier.inference(roi)
                cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (0, 255, 0), 2)
                label = f'{predicted_class}: {probs:.2f}'
                cv2.putText(frame, label, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                treatData(predicted_class)
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
async def inference(request: Request, inference: bool = Form(...), db: Session = Depends(get_db)):
    global inferencing
    try:
        if inference:
            inferencing = True
        else:
            inferencing = False
            batch_number = get_batch_number(db)
            date = get_date()
            add_batches(batch_number, fruit_choice, freshCount, rottenCount, date, db)
            
            return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        # Log or handle the error appropriately
        print("Error in inference route:", e)
    return templates.TemplateResponse("home.html", {"request": request, "inferencing": inferencing})

@app.post('/select_fruit')
async def select_fruit(request: Request, fruit: str = Form(...), inference: bool = Form(...)):
    global inferencing, fruit_choice
    try:
        fruit_choice = fruit
        if inference:
            inferencing = True
        else:
            inferencing = False
            return RedirectResponse(url="/", status_code=303)
    except Exception as e:
        print("Error in inference route:", e)
    return templates.TemplateResponse("home.html", {"request": request, "inferencing": inferencing})


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

def add_batches(batch_number, fruit, fresh, rotten, date, db: Session):
    global freshCount, rottenCount

    db.add(Batches(batch_num=batch_number, fruit=fruit, fresh_count=fresh, rotten_count=rotten, date=date))
    db.commit()
    freshCount,rottenCount = 0,0
    

def get_date():
    return datetime.now().strftime('%m/%d/%Y')

def get_batch_number(db):
    last_batch = db.query(Batches).order_by(desc(Batches.batch_num)).first()
    current_date = int(datetime.now().strftime('%m%d%Y'))

    if last_batch:
        last_batch_date = last_batch.batch_num // 1000
        if last_batch_date == current_date:
            last_batch_number = last_batch.batch_num % 1000 
            next_batch_number = last_batch_number + 1
        else:
            next_batch_number = 1
    else:
        next_batch_number = 1

    return int(f"{current_date:08d}{next_batch_number:03d}")



def most_frequent(List):
    # Filter out occurrences of 'No Fruit' from the list
    filtered_list = [item for item in List if item != 'No Fruit']
    # Return the most frequent element from the filtered list
    return max(set(filtered_list), key=filtered_list.count)

#
# def treatData(fruit_class):
#     global freshCount, rottenCount, fruit_sequence
#     thres = 10

#     fruit_sequence.append(fruit_class)

#     if fruit_class == 'no fruit':
#         if len(fruit_sequence) >= thres and all(fruit == 'no fruit' for fruit in fruit_sequence[-thres:]):
#             fruit_sequence.clear()
#         else:
#             prev_fruit = fruit_sequence[-2] if len(fruit_sequence) > 1 else None
#             if prev_fruit in ['fresh fruit', 'rotten fruit']:
#                 if most_frequent(fruit_sequence) == 'fresh fruit':
#                     freshCount += 1
#                 elif most_frequent(fruit_sequence) == 'rotten fruit':
#                     servo(arduino)
#                     rottenCount += 1
#                 fruit_sequence.clear()

def treatData(fruit_class):
    global freshCount, rottenCount, fruit_sequence
    thres = 10

    fruit_sequence.append(fruit_class)

    if fruit_class == 'No Fruit':
        if len(fruit_sequence) >= thres and all(fruit == 'No Fruit' for fruit in fruit_sequence[-thres:]):
            fruit_sequence.clear()
        else:
            prev_fruit = fruit_sequence[-2] if len(fruit_sequence) > 1 else None
            if prev_fruit in ['Grade 1', 'Grade 2', 'Grade 3']:
                if most_frequent(fruit_sequence) == 'Grade 1' or most_frequent(fruit_sequence) == 'Grade 2':
                    freshCount += 1
                elif most_frequent(fruit_sequence) == 'Grade 3':
                    servo(arduino)
                    rottenCount += 1
                fruit_sequence.clear()


