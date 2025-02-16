import sys
from twocaptcha import TwoCaptcha
import random
import asyncio
import numpy as np
import bezier

# Cấu hình API Key
API_KEY = "c296bdb0140766926a839c5536b49551"
CAPTCHA_IMAGE_PATH = "shein/captcha.jpg"

solver = TwoCaptcha(API_KEY)

def solve_captcha(image_path):
    """ Gửi ảnh CAPTCHA lên 2Captcha và lấy kết quả tọa độ """
    try:
        result = solver.coordinates(image_path)  # Giải CAPTCHA dạng Click
        print("Kết quả CAPTCHA:", result)
        return result
    except Exception as e:
        sys.exit(f"Lỗi giải CAPTCHA: {e}")

async def move_mouse_curve(page, start_x, start_y, end_x, end_y):
    """
    Di chuyển chuột theo đường cong Bezier từ (start_x, start_y) đến (end_x, end_y).
    """
    # Tạo các điểm điều khiển cho đường cong Bezier
    control_points = np.array([
        [start_x, start_x + random.randint(50, 150), end_x + random.randint(-50, 50), end_x],  # Tọa độ x
        [start_y, start_y + random.randint(-100, 100), end_y + random.randint(-50, 50), end_y]  # Tọa độ y
    ])
    
    # Tạo đường cong Bezier
    curve = bezier.Curve(control_points, degree=3)
    
    # Di chuyển chuột theo đường cong
    for t in np.linspace(0, 1, 20):  # Di chuyển qua 20 điểm trên đường cong
        point = curve.evaluate(t)
        x, y = float(point[0]), float(point[1])  # Chuyển đổi ndarray thành float
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.05, 0.1))  # Độ trễ ngẫu nhiên

async def solve_captcha_on_page(page):
    """ Tìm CAPTCHA trên trang, chụp ảnh và gửi lên 2Captcha để giải """

    retry_count = 0
    max_retries = 6  # Số lần thử lại tối đa

    while retry_count < max_retries:
        print(f"🔍 Thử giải CAPTCHA lần {retry_count + 1}...")

        # Chờ captcha hiển thị
        captcha_elem = page.locator(".captcha_click_wrapper")

        if not await captcha_elem.is_visible():
            print("✅ Không thấy CAPTCHA, có thể đã được giải.")
            return True  # Không cần giải CAPTCHA

        await captcha_elem.wait_for(state="visible", timeout=10000)  # Chờ tối đa 10s

        box = await captcha_elem.bounding_box()
        if not box:
            print("⚠️ Không tìm thấy CAPTCHA, thử lại sau.")
            return False

        # Chụp ảnh CAPTCHA
        await captcha_elem.screenshot(path=CAPTCHA_IMAGE_PATH)
        print("📸 Đã chụp CAPTCHA, gửi lên 2Captcha để giải...")

        # Giải CAPTCHA
        result = solve_captcha(CAPTCHA_IMAGE_PATH)
        coordinates_str = result["code"].replace("coordinates:", "")
        coordinates_list = coordinates_str.split(";")

        # Click vào các điểm trên ảnh CAPTCHA với độ trễ ngẫu nhiên
        for coord in coordinates_list:
            x, y = map(int, coord.replace("x=", "").replace("y=", "").split(","))

            # Sử dụng move_mouse_curve để di chuyển chuột đến vị trí click
            await move_mouse_curve(page, box["x"], box["y"], box["x"] + x, box["y"] + y)
            await asyncio.sleep(random.uniform(0.5, 1.5))  # Thêm độ trễ ngẫu nhiên
            await page.mouse.click(box["x"] + x, box["y"] + y)

            delay = random.uniform(2, 3)  # Tạo độ trễ ngẫu nhiên từ 2 đến 3 giây
            print(f"🕒 Đợi {delay:.2f} giây trước khi click tiếp...")
            await asyncio.sleep(delay)

        # Chờ thêm 3 giây trước khi ấn nút "CONFIRM"
        print("🕒 Chờ 3 giây trước khi xác nhận CAPTCHA...")
        await asyncio.sleep(3)

        # Click vào nút "CONFIRM"
        confirm_button = page.locator(".captcha_click_confirm")
        await confirm_button.hover()
        await asyncio.sleep(random.uniform(0.5, 1.5))  # Thêm độ trễ ngẫu nhiên
        await confirm_button.click()

        print("✅ Đã gửi CAPTCHA!")

        # Kiểm tra xem CAPTCHA có còn hay không
        await asyncio.sleep(5)
        if not await captcha_elem.is_visible():
            print("🎉 CAPTCHA đã được giải quyết thành công!")
            return True

        print("⚠️ CAPTCHA chưa được giải, thử lại...")
        retry_count += 1

    print("❌ Không thể giải CAPTCHA sau nhiều lần thử.")
    return False