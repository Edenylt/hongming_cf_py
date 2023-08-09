import time
import pynput.mouse
from pynput.mouse import Listener
import threading
import mss
import mss.tools
from PIL import Image
import win32api
import win32con
import pygame
import chardet
# 初始化音效
pygame.init()
open_sound = pygame.mixer.Sound('open_sound.wav')  # 替换为开启音效文件的路径
close_sound = pygame.mixer.Sound('close_sound.wav')  # 替换为关闭音效文件的路径

is_clicked = False


# 点击一次侧键开始，再点击一次侧键关闭
def key_click(x, y, button, pressed):
    global is_clicked
    if pressed and button == pynput.mouse.Button.x1:
        is_clicked = not is_clicked
        if is_clicked:
            open_sound.play()  # 播放开启音效
        else:
            close_sound.play()  # 播放关闭音效


def read_config_file():
    # 读取配置文件并返回变量的值
    variables = {}
    with open('config.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line:
                key, value = line.split('=')
                variables[key.strip()] = value.strip()
    return variables


# 从配置文件读取变量值
config_variables = read_config_file()

# 使用配置文件中的值修改变量
center_width = int(config_variables.get('x'))
y_1 = int(config_variables.get('y_1'))
y_2 = int(config_variables.get('y_2'))
time_sleep = float(config_variables.get('time_sleep'))


def check_red_color(pixel, min_red_value, max_red_value):
    if (
            min_red_value[0] <= pixel[0] <= max_red_value[0]
            and min_red_value[1] <= pixel[1] <= max_red_value[1]
            and min_red_value[2] <= pixel[2] <= max_red_value[2]
    ):
        return True
    return False


def click_left_button():
    x, y = win32api.GetCursorPos()
    time.sleep(time_sleep)
    # print("点击鼠标")
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


# 获取屏幕尺寸
with mss.mss() as sct:
    # 显示器大小
    monitor_width = 1280
    monitor_height = 720

    # 要截取的区域大小
    capture_width = 200
    capture_height = 200

    # 计算中心位置的坐标
    center_x = monitor_width // 2
    center_y = monitor_height // 2

    # 计算左上角坐标
    x1 = center_x - capture_width // 2
    y1 = center_y - capture_height // 2

    # 计算右下角坐标
    x2 = center_x + capture_width // 2
    y2 = center_y + capture_height // 2

    # 设置monitor字典
    monitor = {"top": y1, "left": x1, "width": capture_width, "height": capture_height}

def run():
    global is_clicked
    # 点击标志变量
    clicking = False
    while True:
        # 获取屏幕截图
        with mss.mss() as sct:
            screenshot = sct.grab(monitor)

        # 将截图转换为PIL图像对象
        pil_image = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")


        # 获取中心区域的像素值
        center_pixels = []
        for x in range(capture_width//2 - center_width // 2, capture_width//2 + center_width // 2):
            for y in range(capture_height//2 + y_1, capture_height//2 + y_2):
                pixel = pil_image.getpixel((x, y))
                center_pixels.append(pixel)

        # 定义红色的RGB值范围
        min_red_rgb = (120, 40, 20)
        max_red_rgb = (240, 80, 80)

        # 判断中心区域是否有符合条件的红色像素，并且按下鼠标左键
        if is_clicked and any(check_red_color(pixel, min_red_rgb, max_red_rgb) for pixel in center_pixels):
            # 如果之前未点击，则开始持续点击鼠标左键
            if not clicking:
                clicking = True
                # print("敌人的名字变成红色，开始红名自动开枪")

        # 如果之前已经开始点击，并且中心区域不再有符合条件的红色像素，则停止点击
        elif clicking:
            clicking = False
            # print("敌人的名字不再是红色，停止点击鼠标左键")

        # 持续点击鼠标左键
        if clicking and is_clicked:
            click_left_button()
        # 每次循环之后稍作延迟
        # time.sleep(0.05)


def mouse_listener():
    with Listener(on_click=key_click) as listener:
        listener.join()


if __name__ == "__main__":
    threading.Thread(target=mouse_listener).start()
    run()
