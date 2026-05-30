import random
import time
from typing import Optional

import pyautogui

from screen import call_iphone, countdown, find_image_on_screen

# 图片路径前缀
IMAGE_PREFIX = "images/qishui/"

# 固定坐标
LIVESTREAM_CLOSE_FALLBACK = (295, 143)

# 循环与延迟配置
MAX_LOOP_COUNT = 90
AD_WAIT_INTERVAL = 5
POST_CLICK_DELAY = 1
REWARD_CLICK_DELAY = 2
MEMBER_UNLOCK_INTERVAL = 3
INIT_COUNTDOWN = 5

# 全局坐标缓存
_coordinates_cache: dict = {}


def get_cached_coordinate(
    *image_paths: str,
    force_refresh: bool = False,
) -> Optional[tuple]:
    """获取缓存的坐标，支持传入多个图片路径，只要一个获取到有效坐标就返回。

    Args:
        *image_paths: 一个或多个图片文件名（不含路径前缀）
        force_refresh: 是否强制刷新缓存

    Returns:
        找到的第一个有效坐标，如果没有找到则返回 None
    """
    for image_name in image_paths:
        image_path = IMAGE_PREFIX + image_name

        if not force_refresh and image_path in _coordinates_cache:
            cached = _coordinates_cache[image_path]
            if cached:
                print(f"使用缓存坐标: {image_path} -> {cached}")
                return cached
            continue

        position = find_image_on_screen(image_path)
        if position:
            _coordinates_cache[image_path] = position
            print(f"缓存坐标: {image_path} -> {position}")
            return position

    return None


def is_finished() -> Optional[tuple]:
    """检查任务是否完成。"""
    return get_cached_coordinate("finished.png")


def qishui_ad() -> None:
    """主流程：启动 iPhone 镜像应用并查找目标图片。"""
    call_iphone()
    countdown(INIT_COUNTDOWN)


def _find_success_position() -> Optional[tuple]:
    """查找成功图片位置（强制刷新）。"""
    return get_cached_coordinate("success.png", "success1.png", force_refresh=True)


def _handle_retry() -> bool:
    """处理广告未加载完成的情况。返回 True 表示已处理。"""
    retry = get_cached_coordinate("retry.png")
    if retry:
        print("广告未加载完成")
        pyautogui.click(retry)
        return True
    return False


def _handle_livestream() -> bool:
    """处理直播界面的情况。返回 True 表示当前处于直播界面。"""
    if not get_cached_coordinate("guan-zhu.png", force_refresh=True):
        return False

    print("进入了直播界面")
    close_pos = get_cached_coordinate("gz-close.png", force_refresh=True)
    if close_pos:
        pyautogui.click(close_pos)
        print(f"已关闭直播 {close_pos}")
    else:
        print("未找到关闭按钮,尝试点击固定位置")
        pyautogui.click(LIVESTREAM_CLOSE_FALLBACK)
    return True


def _try_claim_reward() -> bool:
    """尝试领取奖励并点击喇叭。返回 True 表示成功领取奖励。"""
    reward_pos = get_cached_coordinate("reward.png")
    if not reward_pos:
        print("未找到领取奖励按钮")
        return False

    print(f"领取奖励位置(逻辑坐标): {reward_pos}")
    pyautogui.click(reward_pos)
    time.sleep(REWARD_CLICK_DELAY)

    horn_pos = get_cached_coordinate("speaker.png")
    print(f"喇叭图标位置(逻辑坐标): {horn_pos}")
    if horn_pos:
        print(f"点击喇叭图标(逻辑坐标): {horn_pos}")
        pyautogui.click(horn_pos)
    else:
        print("未找到喇叭图标")
    return True


def loop_process() -> None:
    """主循环：自动点击广告并领取奖励。"""
    count = 0
    day = 0

    while count < MAX_LOOP_COUNT:
        if is_finished():
            print("任务完成")
            break

        position = _find_success_position()
        if not position:
            if _handle_retry():
                continue
            if _handle_livestream():
                continue
            print("广告未播放完毕，继续等待ing")
            time.sleep(AD_WAIT_INTERVAL)
            continue

        print(f"成功图片位置(逻辑坐标): {position}，随机延迟1-5秒")
        countdown(random.randint(1, 5))
        pyautogui.click(position)
        time.sleep(POST_CLICK_DELAY)

        if not _try_claim_reward():
            continue

        count += 1
        print(f"第{count}次循环")
        if count % MEMBER_UNLOCK_INTERVAL == 0:
            day += 1
            print(f"已解锁{day}天会员")
            time.sleep(1)
