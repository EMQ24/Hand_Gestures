import math
import cv2
import mediapipe as mp
import pygame as pg
import sys

# 静态手势的识别类
class StaticHandPose: 
    def __init__(self, **ges_parms): 
        self.angle_list = [None] * 5
        self.thr_angle_c = ges_parms["拇指闭合阈值"]
        self.thr_angle_c_thumb = ges_parms["大拇指闭合阈值"]
        self.thr_angle_o = ges_parms["拇指张开阈值"]
        self.gesture_str = "Unkown"
        pass
    
    def vector2dAngle(self, v1,v2):
        '''
            求解二维向量的角度
        '''
        v1_x=v1[0]
        v1_y=v1[1]
        v2_x=v2[0]
        v2_y=v2[1]
        try:
            angle_= math.degrees(math.acos((v1_x*v2_x+v1_y*v2_y)/(((v1_x**2+v1_y**2)**0.5)*((v2_x**2+v2_y**2)**0.5))))
        except:
            angle_ =65535.
        if angle_ > 180.:
            angle_ = 65535.
        return angle_

    def handAngle(self, hand_):
        '''
            获取对应手相关向量的二维角度,根据角度确定手势
        '''
        angle_list = []
        #---------------------------- thumb 大拇指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[2][0])),(int(hand_[0][1])-int(hand_[2][1]))),
            ((int(hand_[3][0])- int(hand_[4][0])),(int(hand_[3][1])- int(hand_[4][1])))
            )
        angle_list.append(angle_)
        #---------------------------- index 食指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])-int(hand_[6][0])),(int(hand_[0][1])- int(hand_[6][1]))),
            ((int(hand_[7][0])- int(hand_[8][0])),(int(hand_[7][1])- int(hand_[8][1])))
            )
        angle_list.append(angle_)
        #---------------------------- middle 中指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[10][0])),(int(hand_[0][1])- int(hand_[10][1]))),
            ((int(hand_[11][0])- int(hand_[12][0])),(int(hand_[11][1])- int(hand_[12][1])))
            )
        angle_list.append(angle_)
        #---------------------------- ring 无名指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[14][0])),(int(hand_[0][1])- int(hand_[14][1]))),
            ((int(hand_[15][0])- int(hand_[16][0])),(int(hand_[15][1])- int(hand_[16][1])))
            )
        angle_list.append(angle_)
        #---------------------------- pink 小拇指角度
        angle_ = self.vector_2d_angle(
            ((int(hand_[0][0])- int(hand_[18][0])),(int(hand_[0][1])- int(hand_[18][1]))),
            ((int(hand_[19][0])- int(hand_[20][0])),(int(hand_[19][1])- int(hand_[20][1])))
            )
        angle_list.append(angle_)
        return angle_list

    def handGesture(self, angle_list):
        '''
            # 二维约束的方法定义手势
            # fist five gun love one six three thumbup yeah
        '''
        thr_angle = 65.  #手指闭合则大于这个值（大拇指除外）
        thr_angle_thumb = 53.  #大拇指闭合则大于这个值
        thr_angle_s = 49.  #手指张开则小于这个值
        gesture_str = "Unknown"
         # [54,52,65,78,23] -> [1,1,1,1,0]
        if 65535. not in angle_list:
            return gesture_str
        
        angle_key = []
        for i, num in enumerate(angle_list):
            if i == 0:
                if num > self.thr_angle_c_thumb:
                    angle_key.append('1')
                elif num < self.thr_angle_o:
                    angle_key.append('0')
                else: 
                    angle_key.append('-1')
            else: 
                if num > self.thr_angle_c:
                    angle_key.append('1')
                elif num < self.thr_angle_o: 
                    angle_key.append('0')
                else:
                    angle_key.append('-1')
        
        angle_key + ''.join(angle_key)  
                  
        gesture_dict = {
            "[11111]" : "0",
            "[10111]" : "1",
            "[10011]" : "2", 
            "[10001]" : "3",
            "[10000]" : "4",
            "[00000]" : "5",
            "[01110]" : "6",
            # [0,0,0,0,0] : "7",
            "[00111]" : "8",
            # [0,0,0,0,0] : "9",
        }            
        # gesture_dict的对应手指动作
        for key in gesture_dict: 
            if angle_key == key:
                gesture_str = gesture_dict[key]
                return gesture_str
    
    def detect(self, mp_drawing,mp_hands,hands,cap):
        ret,frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame= cv2.flip(frame,1)
        results = hands.process(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if results.multi_handedness:
            for hand_label in results.multi_handedness:
                hand_jugg=str(hand_label).split('"')[1]
                # print(hand_jugg)
                cv2.putText(frame,hand_jugg,(50,200),0,1.3,(225,0,255),1)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                hand_local = []
                for i in range(21):
                    x = hand_landmarks.landmark[i].x*frame.shape[1]
                    y = hand_landmarks.landmark[i].y*frame.shape[0]
                    hand_local.append((x,y))
                if hand_local:
                    angle_list = self.handAngle(hand_local)
                    self.gesture_str = self.handGesture(angle_list)
                    # print(gesture_str)
                    cv2.putText(frame,self.gesture_str,(50,100),0,1.3,(225,0,255),1)
                    
        cv2.imshow('MediaPipe Hands', frame)
        
        if(results.multi_handedness and results.multi_hand_landmarks):
            return hand_jugg,self.gesture_str
        else:
            return None,None
    
    def  drawText(self,content):
        pg.font.init()
        font  =  pg.font.Font(None,200)
        text_sf  =  font.render(content,True,pg.Color(255,255,255),pg.Color(0,0,0))
        return  text_sf
        
    def recognize(self,): 
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.75,
            min_tracking_confidence=0.75)
        cap = cv2.VideoCapture(0)

        number = -1
        digit = 11
        input_act = 0
        oper_act = 0
        output = []
    

ges_parms = {
    "拇指闭合阈值" : 65.,
    "大拇指闭合阈值" : 53.,
    "拇指张开阈值": 49.
}
    
static_hand_pose = StaticHandPose(**ges_parms)
static_hand_pose.recognize()