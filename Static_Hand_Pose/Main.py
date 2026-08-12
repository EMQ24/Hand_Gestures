import cv2
import mediapipe as mp
import math
import time
import sys
import pygame as pg

mp_drawing_styles =  mp.solutions.drawing_styles

def vector_2d_angle(v1,v2):
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

def hand_angle(hand_):
    '''
        获取对应手相关向量的二维角度,根据角度确定手势
    '''
    angle_list = []
    #---------------------------- thumb 大拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[2][0])),(int(hand_[0][1])-int(hand_[2][1]))),
        ((int(hand_[3][0])- int(hand_[4][0])),(int(hand_[3][1])- int(hand_[4][1])))
        )
    angle_list.append(angle_)
    #---------------------------- index 食指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])-int(hand_[6][0])),(int(hand_[0][1])- int(hand_[6][1]))),
        ((int(hand_[7][0])- int(hand_[8][0])),(int(hand_[7][1])- int(hand_[8][1])))
        )
    angle_list.append(angle_)
    #---------------------------- middle 中指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[10][0])),(int(hand_[0][1])- int(hand_[10][1]))),
        ((int(hand_[11][0])- int(hand_[12][0])),(int(hand_[11][1])- int(hand_[12][1])))
        )
    angle_list.append(angle_)
    #---------------------------- ring 无名指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[14][0])),(int(hand_[0][1])- int(hand_[14][1]))),
        ((int(hand_[15][0])- int(hand_[16][0])),(int(hand_[15][1])- int(hand_[16][1])))
        )
    angle_list.append(angle_)
    #---------------------------- pink 小拇指角度
    angle_ = vector_2d_angle(
        ((int(hand_[0][0])- int(hand_[18][0])),(int(hand_[0][1])- int(hand_[18][1]))),
        ((int(hand_[19][0])- int(hand_[20][0])),(int(hand_[19][1])- int(hand_[20][1])))
        )
    angle_list.append(angle_)
    return angle_list

def h_gesture(angle_list):
    '''
        # 二维约束的方法定义手势
        # fist five gun love one six three thumbup yeah
    '''
    thr_angle = 65.  #手指闭合则大于这个值（大拇指除外）
    thr_angle_thumb = 53.  #大拇指闭合则大于这个值
    thr_angle_s = 49.  #手指张开则小于这个值
    gesture_str = "Unknown"
    if 65535. not in angle_list:
        if (angle_list[0]>thr_angle_thumb) and (angle_list[1]>thr_angle) and (angle_list[2]>thr_angle) and (angle_list[3]>thr_angle) and (angle_list[4]>thr_angle):
            gesture_str = "0"
        elif (angle_list[0]>thr_angle_thumb)  and (angle_list[1]<thr_angle_s) and (angle_list[2]>thr_angle) and (angle_list[3]>thr_angle) and (angle_list[4]>thr_angle):
            gesture_str = "1"
        elif (angle_list[0]>thr_angle_thumb)  and (angle_list[1]<thr_angle_s) and (angle_list[2]<thr_angle_s) and (angle_list[3]>thr_angle) and (angle_list[4]>thr_angle):
            gesture_str = "2"
        elif (angle_list[0]>thr_angle_thumb)  and (angle_list[1]<thr_angle_s) and (angle_list[2]<thr_angle_s) and (angle_list[3]<thr_angle_s) and (angle_list[4]>thr_angle):
            gesture_str = "3"
        elif (angle_list[0]>thr_angle_thumb) and (angle_list[1]<thr_angle_s) and (angle_list[2]<thr_angle_s) and (angle_list[3]<thr_angle_s) and (angle_list[4]<thr_angle_s):
            gesture_str = "4"
        elif (angle_list[0]<thr_angle_s) and (angle_list[1]<thr_angle_s) and (angle_list[2]<thr_angle_s) and (angle_list[3]<thr_angle_s) and (angle_list[4]<thr_angle_s):
            gesture_str = "5"
        elif (angle_list[0]<thr_angle_s)  and (angle_list[1]>thr_angle) and (angle_list[2]>thr_angle) and (angle_list[3]>thr_angle) and (angle_list[4]<thr_angle_s):
            gesture_str = "6"
        elif (angle_list[0]<thr_angle_s)  and (angle_list[1]<thr_angle_s) and (angle_list[2]>thr_angle) and (angle_list[3]>thr_angle) and (angle_list[4]>thr_angle):
            gesture_str = "8"
            
            
            
        elif (angle_list[0]>thr_angle_thumb)  and (angle_list[1]<thr_angle_s) and (angle_list[2]>thr_angle) and (angle_list[3]>thr_angle) and (angle_list[4]>thr_angle):
            gesture_str = "G"
                        
            
            
        elif (angle_list[0]>thr_angle_thumb) and (angle_list[1]>thr_angle) and (angle_list[2]>thr_angle) and (angle_list[3]>thr_angle) and (angle_list[4]<thr_angle_s):
            gesture_str = "delete"
        elif (angle_list[0]<thr_angle_s)  and (angle_list[1]>thr_angle) and (angle_list[2]>thr_angle) and (angle_list[3]>thr_angle) and (angle_list[4]>thr_angle):
            gesture_str = "6"
        elif (angle_list[0]>thr_angle_thumb) and (angle_list[1]>thr_angle) and (angle_list[2]<thr_angle_s) and (angle_list[3]<thr_angle_s) and (angle_list[4]<thr_angle_s):
            gesture_str = "OK"
        elif (angle_list[0]<thr_angle_s)  and (angle_list[1]<thr_angle_s) and (angle_list[2]<thr_angle_s) and (angle_list[3]>thr_angle) and (angle_list[4]>thr_angle):
            gesture_str = "Bye"
        elif (angle_list[0]<thr_angle_s)  and (angle_list[1]<thr_angle_s) and (angle_list[2]>thr_angle) and (angle_list[3]>thr_angle) and (angle_list[4]<thr_angle_s):
            gesture_str = "10"
        elif (angle_list[0]>thr_angle_thumb)  and (angle_list[1]<thr_angle_s) and (angle_list[2]>thr_angle) and (angle_list[3]>thr_angle) and (angle_list[4]<thr_angle_s):
            gesture_str = "9"
        
    return gesture_str

def detect(mp_drawing,mp_hands,hands,cap):
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
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
            hand_local = []
            for i in range(21):
                x = hand_landmarks.landmark[i].x*frame.shape[1]
                y = hand_landmarks.landmark[i].y*frame.shape[0]
                hand_local.append((x,y))
            if hand_local:
                angle_list = hand_angle(hand_local)
                gesture_str = h_gesture(angle_list)
                # print(gesture_str)
                cv2.putText(frame,gesture_str,(50,100),0,1.3,(225,0,255),1)
                
    cv2.imshow('MediaPipe Hands', frame)
    
    if(results.multi_handedness and results.multi_hand_landmarks):
        return hand_jugg,gesture_str
    else:
        return None,None
    
    # experiment only
def  drawText(content):
    pg.font.init()
    font  =  pg.font.Font(None,200)
    text_sf  =  font.render(content,True,pg.Color(255,255,255),pg.Color(0,0,0))
    return  text_sf
    
    if __name__ == '__main__':
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                min_detection_confidence=0.75,
                min_tracking_confidence=0.75)
        cap = cv2.VideoCapture(0)
        
        number_L = -1
        number_R = -1
        order = None
        number = -1
        digit = 11
        input_act = 0
        oper_act = 0
        output = []
        
        pg.display.init()
        win = pg.display.set_mode([1500,200])
        win.fill(pg.Color(255,255,255))
        screen_rect = win.get_rect()

        
        while True:
            time.sleep(0)
            hand_jugg, gesture_str = detect(mp_drawing,mp_hands,hands,cap)
                
            
            if(gesture_str in ['0','1','2','3','4','5','6','7','8','9','10']):
                oper_act = 0
                if(number == gesture_str):
                    input_act += 1 # 输入动作的检测
                else:
                    number = gesture_str
            
                if(input_act >= 20)and(len(output) < digit):
                    output.append(number)
                    # serialSend(number)
                    input_act = 0
                    
            if(gesture_str == "delete"):
                input_act = 0
                oper_act += 1
                if(oper_act >= 8):
                    try:
                        output.pop()
                    except:
                        pass
                    oper_act = 0
                    
            if(gesture_str == "OK"):
                oper_act += 1
                if(oper_act >= 20):
                    pass
                    oper_act = 0
            

            display = list(output)
            for i in range(digit - len(display)):
                display.append("_")        
                
            sys.stdout.write('\r')
            sys.stdout.write(''.join(display))
            sys.stdout.flush()
            # print(output)
            txt = drawText("    {}    ".format(''.join(display)))
            win.blit(txt, txt.get_rect(center=screen_rect.center))
            pg.display.update()

            
            
            
            if cv2.waitKey(1) & 0xFF == 27:
                break
            
        cap.release()
        cv2.destroyAllWindows()