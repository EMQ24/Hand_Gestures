# 队列技术

## 1.相近序列重复识别

    措施：每次识别到一种动态手势，立马清空队列

    代码：hand_list = []

    目的：防止相近的序列（相近的序列通常相似）被重复识别为同种动态手势

## 2.相似序列重复识别

    措施1：每次识别到手势之后，设置延迟

    代码：
    if dur > 1:
        orderExecute(ind2label_2[index])
        start_time = time.time()

    目的：由于我们采用的队列长度为20，做某一种手势时，我们做某一动作一般为35-45帧（根据训练集），所以如果最初始的20帧就被识别到，即使队列清空，很有可能在接下来的20帧被识别为同一种手势，所以我们设置识别延迟，防止这样的情况发生

    措施2：修改训练参数：队列长度为30

## tips:

    采用20帧【优点】是，可以识别手势（35-40帧）的 任意有效20帧，【缺点】是，容易识别出错误手势：例如向左滑动时停留时间过长就有可能让队列产生向右滑动的前20帧

        即，可以提高召回率，但是也容易出现假阳性，不过通过以上措施可以解决这个问题

    采用30帧【优点】是，可以防止相似序列重复识别，甚至不需要设置延迟操作，【缺点】是，需要按照训练集做出比较完整标准的手势动作才可以识别

        即，召回率相应降低，但是假阳性的概率会低，精确度上升了

# 动静态隔离技术

## 1.动中隔静

    措施：通过指定手部关键点的移动幅度判断动静态

    代码：if is_hand and abs(hand_list[-1][10][0] - hand_list[-2][10][0]) + abs(hand_list[-1][10][1] - hand_list[-2][10][1]) < 0.01:

        # Dynamic recognition
        elif len(hand_list) == len_hand_list:
            static_count = 0

    目的：防止用户做动态手势时同时激活静态手势识别

## 2.静中隔动

    措施：利用if else，先判别是否是静态(static_count >= 20), 如果有静态，程序将一直堵在静态识别处，不会发生动态识别
    
    不过有意思的是，即使是静态时，队列依然在不断往后更新新的帧，思考，为什么？ Ans:某些动态动作包含一部分静态过程，但可以肯定的是这部分static_count < 20

    注意：static_count 参数的设定一定不能大于与队列长度，不然可能会发生，做静态动作时，还没被判定静态识别，动态队列就已经符合识别条件（达到队列长度20，未静态识别），开始识别，但是问题也不大哈，毕竟你这个时候做的是静态动作，多半也识别不出动态动作，但是，不识别总比有识别出的风险好啊

    代码：            
        # Static recognition     
        if is_hand and abs(hand_list[-1][10][0] - hand_list[-2][10][0]) + abs(hand_list[-1][10][1] - hand_list[-2][10][1]) < 0.01:
            if static_count >= 20:
                is_static = True
                static_ges = static_model.detect(hand_list[-1][:,:2])
                
                orderExecute(static_ges)
                
            else:
                static_count += 1 
        
        # 静态动作已经识别，并且结束以后，要清空队列，静态判别符is_static 归False，静态计数也要归 0
        elif is_static == True:
            is_static = False
            static_count = 0
            hand_list = []
                    
        # Dynamic recognition
        elif len(hand_list) == len_hand_list:
            # 这个操作也必须做，只要进行动态识别，不管是否有识别到，都要将静态计数归0，不然可能会发生这种情况：多个动态动作里包含的静态动作可能会发生累加
            static_count = 0

            # 从非满队列开始做静态动作，中间突然动了几帧，马上保持静态动作，只要在队列满的时候保持的静态动作，也会被识别为某一静态动作
        else:
            static_count = 0

    目的：防止静态动作触发动态识别


# 树莓派部署方案

    tips：训练集是用mediapipe提取的，如果inference使用其他结构提取，不管好与坏，都会和mediapipe提取的关键点有出入，是可能会影响正确率的

## 1.mediapipe
    转不成IR，没办法intel神经棒加速
    但是我们可以拆谷歌的算法，从而转成IR format 用NCS2的openvino加速

## 2.onnx
    识别度高 只有（x，y）
    这个部分只是hand_landmarks

## 3.openpose caffe

    识别度有点差

## 4.Dynamic model

    转IR format 用NCS2的openvino加速