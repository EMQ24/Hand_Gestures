from utils import *
from model import *
import cv2
from tensorflow import keras
import mediapipe as mp
import numpy as np
import re
import time



# 设定队列及参数
hand_list = []
len_hand_list = 20
static_count = 0
is_static = False
ind2label_2 = {0:'向左滑动', 1:'向右滑动', 2:'向上滑动', 3:'向下滑动', 4:'缩小全手', 5:'放大全手'}
dynamic_pose = "unknown"


# 打开摄像头、实例化关键点获取对象
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.4)
# 定义手势识别对象
ges_parms = {
    "拇指闭合阈值" : 65.,
    "大拇指闭合阈值" : 53.,
    "拇指张开阈值" : 49.
}

static_model = StaticHandPose(**ges_parms)
dynamic_model = keras.models.load_model('main/tf_gesture-best.h5')


start_time = time.time()
# 摄像头打开、开始检测
while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        # t = time.time()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)
        
        
        hand_landmarks_array, is_hand = getHandLandmarks(frame, hands)
        
        # 21关键点数据 20长度时间序列长度队列
        if len(hand_list) == 0:
            hand_list = np.array(hand_landmarks_array, dtype=np.float64)[np.newaxis, :, :]
        elif len(hand_list) < len_hand_list:
            hand_list = np.concatenate(
                (hand_list, np.array(hand_landmarks_array, dtype=np.float64)[np.newaxis, :, :]))
        else:
            hand_list = np.concatenate(
                (hand_list[1:], np.array(hand_landmarks_array, dtype=np.float64)[np.newaxis, :, :]))
        
                        
        if len(hand_list) >= 2:
            
            # Static recognition     
            if is_hand and abs(hand_list[-1][10][0] - hand_list[-2][10][0]) + abs(hand_list[-1][10][1] - hand_list[-2][10][1]) < 0.02:
                if static_count >= 15:
                    is_static = True
                    static_ges = static_model.detect(hand_list[-1][:,:2])
                    
                    orderExecute(static_ges, dynamic_pose)
                    
                else:
                    static_count += 1 
            
            elif is_static == True:
                is_static = False
                static_count = 0
                hand_list = []
                        
            # Dynamic recognition
            elif len(hand_list) == len_hand_list:
                static_count = 0
                
                pred, index = gesPredict(hand_list, len_hand_list, dynamic_model)
                
                if pred[index] > 0.95:
                    hand_list = []
                    
                    end_time = time.time()
                    dur = end_time - start_time
                    
                    if dur > 1:
                        dynamic_pose = ind2label_2[index]
                        orderExecute(dynamic_pose, dynamic_pose)
                        start_time = time.time()
                    
            else:
                static_count = 0
                
            # time.sleep(0.25)
            # print(time.time() - t)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            cap.release()
            break
    else:
        cap.release()
cv2.destroyAllWindows()
