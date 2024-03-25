from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import StreamingResponse
from sol import process_vid, get_status
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, BackgroundTasks
import shutil
import uuid
import json
import asyncio
import os
import io
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Allow specific HTTP methods
    allow_headers=["*"],  # Allow all headers
)

rooms = {}

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.mount("/videos/static", StaticFiles(directory="vids/"), name="videos")

class CORSMiddlewareForStaticFiles(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/videos/static"):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response

app.add_middleware(CORSMiddlewareForStaticFiles)

@app.get("/records/{uuid:path}")
async def get_records():
    res = []
    with open(f"vids/records_{uuid.split('.')[0]}.txt", 'r') as file:
        for line in file:
            time, angle, interval = line.split()
            res.append({'time' : time, 'angle' : angle, 'interval' : interval})
    return res

@app.get("/check/{uuid:path}")
async def check_vid(
    uuid : str
):
    process_path = 'vids/processed' + uuid
    if(os.path.exists(process_path) == True):
        return {'processed' : 'true'}
    return {'processed' : 'false'}


@app.get("/video/{uuid:path}")
async def video_endpoint(
    uuid : str
):
    headers = {
        "Connection": "keep-alive",
        "Transfer-Encoding": "chunked"
    }
    path = 'vids/' + uuid
    process_path = 'vids/processed_' + uuid

    if(os.path.exists(process_path) == True):
        with open(process_path, mode="rb") as video_file:
        # Read the content of the video file
            video_content = video_file.read()
            
            # Create a streaming response
            return StreamingResponse(io.BytesIO(video_content), media_type=f"video/{path.split('.')[1]}")
    else:
    # return Response(generate_vid(), mimetype='multipart/x-mixed-replace; boundary=frame')
        return StreamingResponse(generate_vid(path, process_path, send_info_to_room(uuid)), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/processed/{uuid:path}")
async def get_processed_video(
    uuid : str
):
    path = './vids/processed_' + uuid
    if(os.path.exists(path) == True):
        with open(path, mode="rb") as video_file:
            video_content = video_file.read()

            return StreamingResponse(io.BytesIO(video_content), media_type=f"video/{path.split('.')[1]}")
    else:
        return HTTPException(status_code=404,detail='video not found or not processed')
@app.get("/video1")
async def video_endpoint():
    return Response(content=generate_vid(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    unique_filename = str(uuid.uuid4()) + "-" + file.filename
    
    try:
        with open(f'./vids/{unique_filename}', "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        # process_vid(f'./vids/{unique_filename}', f'./vids/processed_{unique_filename}')
    except Exception as e:
        print("ERRROR " , str(e))
        raise HTTPException(status_code=500, detail={"message": str(e)})
   
    background_tasks.add_task(process_vid, f'./vids/{unique_filename}', f'./vids/processed_{unique_filename}')
    
    print("FILENAME " , unique_filename)
    return {"filename": unique_filename}



@app.get("/check-status/{uuid:path}")
async def check_status(uuid : str):
    if uuid.find('.') != -1:
        uuid = uuid.split('.')[0]
    print(" HEY UUID " , uuid)

    return {"status" : get_status(uuid)}


active_connections = set()

@app.websocket("/ws/{uuid:path}")
async def websocket_endpoint(websocket: WebSocket, uuid : str):
    await websocket.accept()
    rooms[uuid] = websocket
    active_connections.add(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            print(f"Received message: {data}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)

def send_info_to_room(room_id):
    async def send_info(info):
        await rooms[room_id].send_text(json.dumps(info))
    return send_info