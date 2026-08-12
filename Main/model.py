import math
import cv2
import mediapipe as mp
import pygame as pg
import sys

# 静态手势的识别类
class StaticHandPose:
    
    def __init__(self, **ges_parms):
        self.angle_key = [None] * 5
        self.thr_angle_c = ges_parms["拇指闭合阈值"]
        self.thr_angle_c_thumb = ges_parms["大拇指闭合阈值"]
        self.thr_angle_o = ges_parms["拇指张开阈值"]
        self.gesture_str = "Unknown"
    
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
        angle_ = self.vector2dAngle(
            ((float(hand_[0][0])- float(hand_[2][0])),(float(hand_[0][1])-float(hand_[2][1]))),
            ((float(hand_[3][0])- float(hand_[4][0])),(float(hand_[3][1])- float(hand_[4][1])))
            )
        angle_list.append(angle_)
        #---------------------------- index 食指角度
        angle_ = self.vector2dAngle(
            ((float(hand_[0][0])-float(hand_[6][0])),(float(hand_[0][1])- float(hand_[6][1]))),
            ((float(hand_[7][0])- float(hand_[8][0])),(float(hand_[7][1])- float(hand_[8][1])))
            )
        angle_list.append(angle_)
        #---------------------------- middle 中指角度
        angle_ = self.vector2dAngle(
            ((float(hand_[0][0])- float(hand_[10][0])),(float(hand_[0][1])- float(hand_[10][1]))),
            ((float(hand_[11][0])- float(hand_[12][0])),(float(hand_[11][1])- float(hand_[12][1])))
            )
        angle_list.append(angle_)
        #---------------------------- ring 无名指角度
        angle_ = self.vector2dAngle(
            ((float(hand_[0][0])- float(hand_[14][0])),(float(hand_[0][1])- float(hand_[14][1]))),
            ((float(hand_[15][0])- float(hand_[16][0])),(float(hand_[15][1])- float(hand_[16][1])))
            )
        angle_list.append(angle_)
        #---------------------------- pink 小拇指角度
        angle_ = self.vector2dAngle(
            ((float(hand_[0][0])- float(hand_[18][0])),(float(hand_[0][1])- float(hand_[18][1]))),
            ((float(hand_[19][0])- float(hand_[20][0])),(float(hand_[19][1])- float(hand_[20][1])))
            )
        angle_list.append(angle_)
        return angle_list

    def handGesture(self, angle_list):
        '''
        # 二维约束的方法定义手势
        # fist five gun love one six three thumbup yeah
        '''
        gesture_str = "Unknown"
        # [54,52,65,78,23] -> [1,1,1,1,0]
        if 65535. in angle_list:
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
        
        angle_key = ''.join(angle_key)
        
        gesture_dict = {
            "11111" : "continue",
            "10111" : "1",
            "10011" : "2",
            "10001" : "3",
            "10000" : "volumedown",
            "00000" : "volumeup",
            "11110" : "cancel",
            "11000" : "confirm"
            
        }
        
        for key in gesture_dict:
            if angle_key == key:
                gesture_str = gesture_dict[key]
                break
        return gesture_str
        
    def detect(self, hand_list):
        angle_list = self.handAngle(hand_list)
        self.gesture_str = self.handGesture(angle_list)
        
        return self.gesture_str



if __name__ == "__main__":
    ges_parms = {
        "拇指闭合阈值" : 65.,
        "大拇指闭合阈值" : 53.,
        "拇指张开阈值" : 49.
    }


    static_hand_pose = StaticHandPose(**ges_parms)
    static_hand_pose.recognize()

