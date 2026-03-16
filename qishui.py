import time
import random
import pyautogui


from screen import find_image_on_screen,countdown,click_qi_shui_icon,call_iphone

# 全局坐标缓存字典
COORDINATES_CACHE = {}

def get_cached_coordinate(*image_paths, force_refresh=False):
    """
    获取缓存的坐标，支持传入多个图片路径，只要一个获取到有效坐标就返回
    参数:
        *image_paths: 可变参数，传入一个或多个图片文件名（不含路径前缀）
        force_refresh: 是否强制刷新缓存
    返回:
        找到的第一个有效坐标，如果没有找到则返回None
    """ 
    prefix = "images/qishui/"
    for image_name in image_paths:
        image_path = prefix + image_name
        if force_refresh or image_path not in COORDINATES_CACHE:
            position = find_image_on_screen(image_path)
            if position:
                COORDINATES_CACHE[image_path] = position
                print(f"缓存坐标: {image_path} -> {position}")
                return position
        else:
            # 从缓存中获取
            cached_position = COORDINATES_CACHE[image_path]
            if cached_position:
                print(f"使用缓存坐标: {image_path} -> {cached_position}")
                return cached_position
    return None


def is_finished():
    return get_cached_coordinate("finished.png")

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
        position = get_cached_coordinate("success.png", "success1.png",force_refresh=True)
        if not position:
            # 判断是否广告未成功加载
            retry = get_cached_coordinate("retry.png")
            if retry:
                print("广告未加载完成")
                pyautogui.click(retry)
                continue
            # 判断是否在直播界面
            if get_cached_coordinate("guan-zhu.png",force_refresh=True):
                print("进入了直播界面")
                # 直播界面，查找关闭按钮
                position = get_cached_coordinate("gz-close.png",force_refresh=True)
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
        reward_position = get_cached_coordinate("reward.png", "reward1.png")
        if reward_position:
            print(f"领取奖励位置(逻辑坐标): {reward_position}")
            pyautogui.click(reward_position)
            time.sleep(2)
        else:
            print("未找到领取奖励按钮")
            continue
        # 查找喇叭图标

        horn_position = get_cached_coordinate("speaker.png")
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
