# 原始：https://github.com/mar1nho/twitter_scrapper_delete，经chatgpt修改

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

USERNAME = input("Enter your X username: ")
PASSWORD = input("Enter your password: ")
PROFILE_URL = f"https://x.com/{USERNAME}/with_replies"

MAX_WAIT = 10
SCROLL_PAUSE = 2
MAX_SCROLLS = 50  # 避免无限滚动，可自行调整

def connect():
    options = webdriver.EdgeOptions()
    options.use_chromium = True
    options.add_argument('--disable-dev-shm-usage')
    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service, options=options)
    driver.set_page_load_timeout(30)
    return driver

def login(driver):
    driver.get("https://x.com/login")
    wait = WebDriverWait(driver, MAX_WAIT)
    try:
        user = wait.until(EC.element_to_be_clickable((By.NAME, "text")))
        user.send_keys(USERNAME); user.send_keys("\n")
        pwd = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
        pwd.send_keys(PASSWORD); pwd.send_keys("\n")
        time.sleep(5)
    except Exception as e:
        print("登录失败：", e)
        driver.quit()
        exit()

def cancel_retweets(driver):
    wait = WebDriverWait(driver, MAX_WAIT)
    driver.get(PROFILE_URL)
    time.sleep(5)
    total_undone = 0
    scrolls = 0
    seen = set()

    while scrolls < MAX_SCROLLS:
        buttons = driver.find_elements(By.CSS_SELECTOR, "[data-testid='unretweet']")
        new_buttons = [b for b in buttons if b not in seen]
        if not new_buttons:
            #driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
            driver.execute_script("window.scrollBy(0, 500);")
            scrolls += 1
            time.sleep(SCROLL_PAUSE)
            continue

        for btn in new_buttons:
            try:
                seen.add(btn)
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                driver.execute_script("arguments[0].click();", btn)
                # 等待并点击确认取消转推
                confirm = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='unretweetConfirm']")))
                driver.execute_script("arguments[0].click();", confirm)
                total_undone += 1
                print(f"已取消 {total_undone} 条转推")
                time.sleep(1)
            except Exception as e:
                print("取消转推出错：", e)
        # 处理完一批后继续滚动加载更多
        #driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(SCROLL_PAUSE)

    print(f"\n完成！共取消 {total_undone} 条转推。")

if __name__ == "__main__":
    drv = connect()
    login(drv)
    cancel_retweets(drv)
    drv.quit()
