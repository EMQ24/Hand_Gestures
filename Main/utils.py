import cv2
import numpy as np
import tensorflow as tf
import pyautogui
import time
import re

def getHandLandmarks(frame, hands):
    
        results = hands.process(frame)

        # 得到手部21关键点数据
        if results.multi_handedness:
            hand_landmarks_array = []
            for hand_label, hand_landmarks in zip(results.multi_handedness, results.multi_hand_landmarks):
                hand_landmarks = str(hand_landmarks.landmark)[1:-1]
                hand_landmarks = re.findall("\d+\.\d+", hand_landmarks)

                for i in range(len(hand_landmarks)):
                    if i % 3 == 0:
                        hand_landmarks_array.append(
                            [hand_landmarks[i], hand_landmarks[i + 1], hand_landmarks[i + 2]])
            is_hand = True
            
        # 如果没得到关键点数据，全部补0
        else:
            hand_landmarks_array = np.zeros((21, 3), dtype=np.float64)
            is_hand = False

        return hand_landmarks_array, is_hand
        
def gesPredict(hand_list, len_hand_list, model):
    
    hand_tensor = tf.convert_to_tensor(hand_list, dtype='float32')   # [20, 21, 3]
    hand_tensor = tf.reshape(hand_tensor, [20, -1])
    data = hand_tensor
    data = tf.expand_dims(data, 0)
    data = tf.split(data, len_hand_list, axis=1)
    data = tf.reshape(data, [1, len_hand_list, -1])
    output = model.predict(data, verbose=0)
    
    pred = output[0]
    index = np.argmax(pred)
    
    return pred, index

def orderExecute(order, dynamic_pose):
    if order == 'volumedown':
        pyautogui.keyDown('volumedown')
        print('volumedown')
    elif order == 'volumeup':
        pyautogui.press('volumeup')
        print('volumeup')
    elif order == 'continue':
        KEY = {
            "向左滑动" : "right",
            "向右滑动" : "left",
            "向上滑动" : "up",
            "向下滑动" : "down",
        }
        if dynamic_pose in KEY.keys():
            pyautogui.press(KEY[dynamic_pose])
            print(dynamic_pose)
            time.sleep(0.05)
        
        
    elif order == 'cancel':
        pyautogui.press('esc')
        print('cancel')
        time.sleep(1)
    elif order == 'confirm':
        pyautogui.press('enter')
        print('confirm')
        time.sleep(1)
    
        
    elif order == '向左滑动':
        pyautogui.press('right')
        print('向左滑动')
    elif order == '向右滑动':
        pyautogui.press('left')
        print('向右滑动')
    elif order == '向上滑动':
        pyautogui.press('up')
        print('向上滑动')
    elif order == '向下滑动':
        pyautogui.press('down')
        print('向下滑动')
    
    elif order == '缩小全手':
        pyautogui.hotkey('win', 'd')
        print('home')
    elif order == '放大全手':
        pyautogui.press('win')
        print('choose')