from multiprocessing.spawn import import_main_path
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import yaml
from yaml.loader import SafeLoader
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Car:
    year = None
    kms = None
    city = None
    seats = None
    power = None
    color = None
    fuel = None
    seats = None
    label = None
    consumption = None
    contamination = None
    max_speed = None
    acceleration = None
    weight = None
    tank_capacity = None

    def __init__(self, raw_data, classified_data):
        pass

with open('values.yaml') as f:
    values = yaml.load(f, Loader=SafeLoader)
    print(values)
 
options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = uc.Chrome()
driver.maximize_window()
 

#Build url
url = 'https://www.coches.net/segunda-mano/?'
for key, value in values['filters'].items():
    url += key + '=' + str(value) +'&'

url = url[:-1]


driver.get(url)
time.sleep(2)
#Click cookies
driver.find_element(By.XPATH, "//button[span[contains(text(), 'Aceptar')]]").click()
time.sleep(2)



def get_car_raw_data():
    raw_data = []
    time.sleep(4)
    #WebDriverWait(driver, 30).until(EC.visibility_of_element_located(By.CLASS_NAME, "#root > div > div.mt-AdvertisingRoadblock-inner > div.mt-App.mt-App--withNoPaddingTop > main"))
    raw_items = driver.find_elements(By.CSS_SELECTOR, '#root > div > div.mt-AdvertisingRoadblock-inner > div.mt-App.mt-App--withNoPaddingTop > main > div > div.mt-PanelAdDetails > div:nth-child(1) > ul > li')
    for raw_item in raw_items:
        raw_data.append(raw_item.text)
    raw_data = list(map(lambda x: ''.join(x.splitlines()), raw_data))
    return raw_data

def select_car(element):
    link = element.get_attribute('href')
    driver.execute_script(f'window.open("{link}","_blank");')
    driver.switch_to.window(driver.window_handles[1])
    raw_data = get_car_raw_data()


cars = []
main_window = driver.current_window_handle
cars_items = driver.find_elements(By.CSS_SELECTOR, 'div > div.sui-AtomCard.sui-AtomCard--responsive > div.sui-AtomCard-info > a')

for car_item in cars_items:
    select_car(car_item)




driver.close()