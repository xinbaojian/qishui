import subprocess
import time
import cv2
import numpy as np
from PIL import Image, ImageGrab
import os
import pyautogui

# 执行AppleScript
# 使用 stdin 传递脚本，避免 -e 多行/转义问题，并开启 check 以捕获非 0 退出码
# 同时改用应用的 Bundle ID（com.apple.iPhoneMirroring）来激活应用，
# 再由 System Events 通过动态获取到的应用名称进行 UI 脚本操作，避免本地化名称差异导致的找不到应用问题。
def run_applescript(script: str) -> None:
    try:
        completed = subprocess.run(
            ["osascript"],
            input=script.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        if completed.stdout:
            print(completed.stdout.decode("utf-8", errors="ignore").strip())
    except subprocess.CalledProcessError as e:
        err_out = e.stderr.decode("utf-8", errors="ignore").strip()
        print("AppleScript 执行失败:")
        print(err_out or str(e))
    except Exception as e:
        print(f"执行AppleScript时发生未知错误: {e}")


def call_iphone():
    # 通过 Bundle ID 获取应用名称，保证在不同语言环境下都能找到正确的进程名称
    # 然后激活应用，并将第一个窗口移动到指定位置
    apple_script = """
        -- 通过 Bundle ID 获取应用当前语言环境下的名称
        set appName to name of application id "com.apple.ScreenContinuity"
        
        -- 激活应用（通过 Bundle ID，避免本地化名称差异）
        tell application id "com.apple.ScreenContinuity"
            activate
        end tell
        
        -- 使用 UI 脚本移动窗口位置
        tell application "System Events"
            tell process appName
                try
                    set position of window 1 to {275, 145}
                on error errMsg number errNum
                    -- 如果窗口不存在或无权限，输出更清晰的错误提示
                    error "无法设置窗口位置: " & errMsg & " (" & errNum & ")"
                end try
            end tell
        end tell
    """
    run_applescript(apple_script)


def find_image_on_screen(template_path, threshold=0.8, window_bounds=None):
    """
    在屏幕上查找图片模板的位置
    
    Args:
        template_path: 模板图片路径
        threshold: 匹配阈值，范围0-1，值越高表示匹配要求越严格
        window_bounds: 可选，(x1, y1, x2, y2) 屏幕逻辑坐标，用于限定在该窗口内匹配
    
    Returns:
        tuple: (x, y) 逻辑坐标，如果未找到返回 None
    """
    # 检查图片文件是否存在
    if not os.path.exists(template_path):
        print(f"错误：图片文件不存在 - {template_path}")
        return None
    
    # 获取屏幕逻辑尺寸（point）
    screen_width, screen_height = pyautogui.size()
    
    # 截取当前屏幕（PIL Image，通常为像素尺寸，Retina 下为 2x）
    screenshot = pyautogui.screenshot()
    shot_w, shot_h = screenshot.size
    
    # 计算缩放比例（像素/逻辑点）
    scale_x = (shot_w / screen_width) if screen_width else 1.0
    scale_y = (shot_h / screen_height) if screen_height else 1.0

    # 转为 OpenCV BGR
    screenshot_np = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    # 读取模板图片
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    
    if template is None:
        print(f"错误：无法读取模板图片 - {template_path}")
        return None
    
    # 模板图片尺寸
    template_h, template_w = template.shape[:2]

    # 计算匹配用的图像与坐标偏移
    use_roi = False
    rx1 = ry1 = 0
    match_img = screenshot_bgr

    if window_bounds and isinstance(window_bounds, tuple) and len(window_bounds) == 4:
        x1, y1, x2, y2 = window_bounds
        if x2 > x1 and y2 > y1:
            # 将窗口逻辑边界映射到截图像素坐标
            rx1 = max(0, int(round(x1 * scale_x)))
            ry1 = max(0, int(round(y1 * scale_y)))
            rx2 = min(shot_w, int(round(x2 * scale_x)))
            ry2 = min(shot_h, int(round(y2 * scale_y)))
            if rx2 > rx1 and ry2 > ry1:
                match_img = screenshot_bgr[ry1:ry2, rx1:rx2]
                use_roi = True

    # 使用模板匹配（在 ROI 或全屏上）
    result = cv2.matchTemplate(match_img, template, cv2.TM_CCOEFF_NORMED)
    
    # 找到最大匹配值的位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # 检查最大匹配值是否超过阈值
    if max_val >= threshold:
        # 计算匹配区域的中心像素坐标（相对全屏像素）
        center_x_px = max_loc[0] + template_w // 2 + (rx1 if use_roi else 0)
        center_y_px = max_loc[1] + template_h // 2 + (ry1 if use_roi else 0)

        # 转换为屏幕逻辑坐标
        logical_x = int(round(center_x_px / scale_x))
        logical_y = int(round(center_y_px / scale_y))
        
        # 返回逻辑坐标，便于后续用 pyautogui.click
        return (logical_x, logical_y)
    else:
        return None

def is_finished():
    return find_image_on_screen("finished.png")
def main_process():
    """
    主流程：启动iPhone镜像应用并查找目标图片
    """
    print("正在启动iPhone镜像应用...")
    call_iphone()
    
    print("等待应用完全加载...")
    time.sleep(1)
    loop_process()
    
def loop_process():
    count = 0
    day = 0
    while count < 30:
        if is_finished():
            print("任务完成")
            break
        # 查找图片位置（在窗口内优先匹配）
        position = find_image_on_screen("success.png")
        if not position:
            # 判断是否在直播界面
            if find_image_on_screen("guan-zhu.png"):
                print("进入了直播界面")
                # 直播界面，查找关闭按钮
                position = find_image_on_screen("gz-close.png")
                if position:
                    pyautogui.click(position)
                    print("已关闭直播")
                    continue
                else:
                    print("未找到关闭按钮")
                continue
            print("广告未播放完毕，继续等待ing")
            time.sleep(5)
            continue
        print(f"成功图片位置(逻辑坐标): {position}")
        pyautogui.click(position)
        time.sleep(1)
        # 查找并点击领取奖励
        reward_position = find_image_on_screen("reward.png")
        if reward_position:
            print(f"领取奖励位置(逻辑坐标): {reward_position}")
            pyautogui.click(reward_position)
            time.sleep(2)
        else:
            print("未找到领取奖励按钮")
        # 查找喇叭图标

        horn_position = find_image_on_screen("speaker.png")
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
            time.sleep(30)


if __name__ == '__main__':
    # 可以选择只调用iPhone应用，或者执行完整流程
    # call_iphone()  # 仅启动应用
    main_process()  # 完整流程：启动应用 + 截图 + 图像匹配
