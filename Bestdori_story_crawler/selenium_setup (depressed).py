import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# setup
DATA_PATH = 'D:\\Workspace\\test\\selenium\\User Data'
URL1 = 'https://bestdori.com/info/events/1'
URL2 = 'https://bestdori.com/tool/storyviewer/event/cn/1/1/'
URL3 = 'https://bestdori.com/info/events/-1'
###

edge_options = webdriver.EdgeOptions()
edge_options.add_argument(f'user-data-dir={DATA_PATH}')
# edge_options.add_argument("profile-directory=Profile 1")

driver = webdriver.Edge(options=edge_options)
wait = WebDriverWait(driver, 10)

driver.get(URL1)

# Open a new window
driver.execute_script("window.open('');")
# Switch to the new window
driver.switch_to.window(driver.window_handles[1])
driver.get(URL2)

# Open a new window
driver.execute_script("window.open('');")
# Switch to the new window
driver.switch_to.window(driver.window_handles[2])
driver.get(URL3)

time.sleep(30)

driver.switch_to.window(driver.window_handles[2])
bad = driver.find_element(By.CSS_SELECTOR, 'div.m-b-l.has-text-centered div.title.is-4')
print(bad.text)  # '找不到活动'

driver.switch_to.window(driver.window_handles[1])
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.m-b-xs.fg-text')))
story = driver.find_element(By.CSS_SELECTOR, 'div.p-tb-l')
print(story.text[:100])

driver.switch_to.window(driver.window_handles[0])
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.title.is-5')))
abstrct = driver.find_element(By.CSS_SELECTOR, '#Stories+div')
print(abstrct.text[:100])

links = driver.find_elements(By.CSS_SELECTOR, '#Stories+div>a')
for link in links:
    print(link.get_attribute('href'))
