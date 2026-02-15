import time
import random
import pyautogui


from screen import find_image_on_screen,countdown,click_qi_shui_icon,call_iphone

def is_finished():
    return find_image_on_screen("images/qishui/finished.png")

def qishui_ad():
    """
    主流程：启动iPhone镜像应用并查找目标图片
    """
    # click_qi_shui_icon()
    call_iphone()
    countdown(5)

    
    # loop_process()
    
def loop_process():
    count = 0
    day = 0
    while count < 90:
        if is_finished():
            print("任务完成")
            break
        # 查找图片位置（在窗口内优先匹配）
        position = find_image_on_screen("images/qishui/success.png")
        if not position:
            position = find_image_on_screen("images/qishui/success1.png")
        if not position:
            # 判断是否广告未成功加载
            retry = find_image_on_screen("images/qishui/retry.png")
            if retry:
                print("广告未加载完成")
                pyautogui.click(retry)
                continue
            # 判断是否在直播界面
            if find_image_on_screen("images/qishui/guan-zhu.png"):
                print("进入了直播界面")
                # 直播界面，查找关闭按钮
                position = find_image_on_screen("images/qishui/gz-close.png")
                if position:
                    pyautogui.click(position)
                    print(f"已关闭直播 {position}")
                    continue
                else:
                    print("未找到关闭按钮,尝试点击固定位置(295,143)")
                    pyautogui.click((295, 143))
                continue
            print("广告未播放完毕，继续等待ing")
            time.sleep(5)
            continue
        print(f"成功图片位置(逻辑坐标): {position} ,随机延迟1-5秒")
        sec = random.randint(1, 5)
        countdown(sec)
        pyautogui.click(position)
        time.sleep(1)
        # 查找并点击领取奖励
        reward_position = find_image_on_screen("images/qishui/reward.png")
        if not reward_position:
            reward_position = find_image_on_screen("images/qishui/reward1.png")
        if reward_position:
            print(f"领取奖励位置(逻辑坐标): {reward_position}")
            pyautogui.click(reward_position)
            time.sleep(2)
        else:
            print("未找到领取奖励按钮")
            continue
        # 查找喇叭图标

        horn_position = find_image_on_screen("images/qishui/speaker.png")
        print(f"喇叭图标位置(逻辑坐标): {horn_position}")
        if horn_position:
            print(f"点击喇叭图标(逻辑坐标): {horn_position}")
            pyautogui.click(horn_position)
        else:
            print("未找到喇叭图标")
        count += 1
        print(f"第{count}次循环")
        # count 对 3 取余等于0
        if count % 3 == 0:
            day += 1
            print(f"已解锁{day}天会员")
            time.sleep(1)
