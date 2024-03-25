import cv2
import mediapipe as mp
import numpy as np
import multiprocessing
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
import time
import base64
import asyncio
from analyze import dofilter, find_depth, find_pitfalls
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose




def calculate_angle(a,b,c):
    a = np.array(a) 
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    # print(np.degrees(angle))
    return np.degrees(angle) 


loading_precent = {}

    
def get_status(path):
    
    if not (path in loading_precent):
        return 0
    return loading_precent[path]

async def process_vid(path, processed_path):
    ext_parts = path.split('.')
    ext = ext_parts[len(ext_parts)-1]
    without_ext = ext_parts[len(ext_parts)-2]
    parts = without_ext.split('/')
    
    print("PARTS " ,  parts , " WITHOUT EXT " , without_ext)
    
    uuid = parts[len(parts)-1]
    

    resolution = (640, 360)

    cap = cv2.VideoCapture(path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


    out = cv2.VideoWriter(processed_path, -1, 20.0, resolution)

    print("RECRODS TXT \n\n", path)

    
    records_txt = open("vids/records_" + parts[len(parts)-1] + '.txt', "a");

    print("\n\n\nHEY PROCESSS\n\n\n")
    print( " UUID " , uuid)
    angles = []
    pitfalls_found = 0
    have_reps = set()
    frames = 0
    frame_length = 3 / 20.0

    sum_angle = 0
    sum_time = 0
    reps = 0

    def write_records(arr):
        nonlocal frames
        nonlocal frame_length
        for el in arr:
            records_txt.write(str(frame_length*frames) + ' ' +str(el['angle']) + ' ' + str(el['interval']) + '\n')

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        try:
            while cap.isOpened():
                frames += 1
                loading_precent[uuid] = frames / total_frames * 100
                push = []
                ret, frame = cap.read()
                

                frame = cv2.resize(frame , resolution)
                
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image)
            
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                angle = 0

                show = []
                fps = cap.get(cv2.CAP_PROP_FPS)
                # frame_length = 1 / fps
                try:
                    landmarks = results.pose_landmarks.landmark
                    
                    anckle = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].z]
                    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].z]
                    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].z]
                
                    show = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value], landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value], landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]]
                    if(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].z < landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z):
                        anckle = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z]
                        knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].z]
                        hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].z]
                        show = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value], landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value], landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]]
                    
                    angle = calculate_angle(anckle, hip, knee)
                 
                    angles.append(angle)
                 
                    filtered = np.copy(angles)
                    filtered = dofilter(filtered, 10)
                    pitfalls = find_pitfalls(filtered)
                 
                    for pitfalls_found in range(len(pitfalls)):
                        if( pitfalls[pitfalls_found] in have_reps):
                            continue
                        done = False
                        for el in have_reps:
                            if(abs(el - pitfalls[pitfalls_found]) <= 20):
                                done = True
                        if(done):
                            continue
                        res = find_depth(filtered, pitfalls[pitfalls_found])
                        if(res != False):
                            have_reps.add(pitfalls[pitfalls_found])
                            angle_filtered, interval = res
                            push.append({'angle' : angle_filtered, 'interval' : interval * frame_length})
                        pitfalls_found += 1
                        print("pitfall found " , pitfalls_found)
                    cv2.putText(image, str(filtered[-1]), tuple(np.multiply((hip[0], hip[1]), [640, 360]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                        mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                        mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                        )  
                except Exception as e:
                    print("ERROR ", e)
                    pass
               
                
                for rep in push:
                    reps += 1
                    sum_time += rep['interval']
                    sum_angle += rep['angle']   
                try:
                    cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
            
        
                    cv2.putText(image, 'REPS', (15,12), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1, cv2.LINE_AA)
                    cv2.putText(image, str(reps), 
                                (10,60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
                    
                    # Stage data
                    cv2.putText(image, 'ANGLE', (65,12), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1, cv2.LINE_AA)
                    cv2.putText(image, "{:.1f}".format(0 if reps == 0 else sum_angle/reps), 
                                (60,60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)

                    cv2.putText(image, 'TIME', (150,12), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1, cv2.LINE_AA)
                    cv2.putText(image, "{:.1f}".format(0 if reps == 0 else sum_time/reps), 
                                (150,60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
                except Exception as e:
                    print("ERROR for PUTTING TEXT " , str(e))
                
                out.write(image)
                
                try:
                    if(len(push) > 0):
                        write_records(push)
                    await asyncio.sleep(0.0001)
                except Exception as e:
                    print("some erorr" , e)
                
        except Exception as e:
            loading_precent[uuid] = True
            records_txt.close()
            out.release()
    loading_precent[uuid] = True
    records_txt.close()
    out.release()




async def generate_vid_1(path, processed_path, send_info, save_vid = False):
    resolution = (640, 360)
    real_time = False

    cap = cv2.VideoCapture(path)
    
    out = cv2.VideoWriter(processed_path, -1, 20.0, resolution)
    records_txt = open("vids/records_" + path.split('.')[0].split('/')[1] + '.txt', "a");

    angles = []
    pitfalls_found = 0
    have_reps = set()
    frames = 0
    frame_length = 3 / 20.0

    def write_records(arr):
        nonlocal frames
        nonlocal frame_length
        for el in arr:
            records_txt.write(str(frame_length*frames) + ' ' +str(el['angle']) + ' ' + str(el['interval']) + '\n')

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        try:
            while cap.isOpened():
                frames += 1
                push = []
                ret, frame = cap.read()
                

                frame = cv2.resize(frame , resolution)
                
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image)
            
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                angle = 0

                show = []
                fps = cap.get(cv2.CAP_PROP_FPS)
                # frame_length = 1 / fps
                try:
                    landmarks = results.pose_landmarks.landmark
                    
                    anckle = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].z]
                    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].z]
                    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].z]
                
                    show = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value], landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value], landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]]
                    if(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].z < landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z):
                        anckle = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].z]
                        knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].z]
                        hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].z]
                        show = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value], landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value], landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]]
                    
                    angle = calculate_angle(anckle, hip, knee)
                 
                    angles.append(angle)
                 
                    filtered = np.copy(angles)
                    filtered = dofilter(filtered, 10)
                    pitfalls = find_pitfalls(filtered)
                 
                    for pitfalls_found in range(len(pitfalls)):
                        if( pitfalls[pitfalls_found] in have_reps):
                            continue
                        done = False
                        for el in have_reps:
                            if(abs(el - pitfalls[pitfalls_found]) <= 20):
                                done = True
                        if(done):
                            continue
                        res = find_depth(filtered, pitfalls[pitfalls_found])
                        if(res != False):
                            have_reps.add(pitfalls[pitfalls_found])
                            angle_filtered, interval = res
                            push.append({'angle' : angle_filtered, 'interval' : interval * frame_length})
                        pitfalls_found += 1
                        print("pitfall found " , pitfalls_found)
                    cv2.putText(image, str(filtered[-1]), tuple(np.multiply((hip[0], hip[1]), [640, 360]).astype(int)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)
                    mp_drawing.draw_landmarks(image, landmarks, mp_pose.POSE_CONNECTIONS,
                                        mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                        mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                        )  
                except Exception as e:
                    print("ERROR ", e)
                    pass
                frame_name = "./framevideo.jpg"
          
                cv2.imwrite(frame_name, image) 
                out.write(image)


                fra = open(frame_name,'rb').read()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + fra + b'\r\n')
                
                try:
                    if(len(push) > 0):
                        write_records(push)
                        await send_info(push)
                except Exception as e:
                    print("some erorr" , e)
                    
                await asyncio.sleep(0.001)

        except Exception as e:
            records_txt.close()
            out.release()

    records_txt.close()
    out.release()
