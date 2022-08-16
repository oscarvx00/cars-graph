from multiprocessing.spawn import import_main_path
import time
from tokenize import Number
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import yaml
from yaml.loader import SafeLoader
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy


def get_provinces(filepath):
    mData = []
    with open(filepath) as file:
        data = json.load(file)
        for item in data:
            mData.append(item['fields']['provincia'])
    return mData

class Car:
    year = None
    kms = None
    city = None
    seats = None
    power = None
    color = None
    fuel = None
    doors = None
    seats = None
    label = None
    consumption = None
    contamination = None
    max_speed = None
    acceleration = None
    weight = None
    tank_capacity = None
    price = None
    url = None

    def __init__(self, raw_data, classified_data):
        for item in raw_data:
            if item.endswith('Puertas'):
                self.doors = int(item.split(' ')[0])
            elif item.endswith('Plazas'):
                self.seats = int(item.split(' ')[0])
            elif item.endswith('km'):
                self.kms = int(item.split(' ')[0].replace('.', ''))
            elif item.endswith('cv'):
                self.power = int(item.split(' ')[0])
            elif item.endswith('gr/km'):
                self.contamination = int(item.split(' ')[0])
            elif not item.endswith('cc') and item >= '1990' and item <= '2023':
                self.year = int(item)
            elif item in ['Diesel', 'Gasolina']:
                self.fuel = item
            elif item in provinces_array:
                self.city = item


#req_proxy = RequestProxy()
#proxies = req_proxy.get_proxy_list()

with open('values.yaml') as f:
    values = yaml.load(f, Loader=SafeLoader)
    print(values)

provinces_array = get_provinces('provincias-espanolas.json')
 
options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
#options.add_argument('--disable-dev-shm-usage')
opt = uc.ChromeOptions()
opt.add_argument('--disable-popup-blocking')
#opt.add_argument(f'--proxy-server={proxies[0].get_address()}')
driver = uc.Chrome(options=opt)
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

def get_classified_data():
    data = {}
    try:
        el = driver.find_element(By.XPATH, "//div[@class='mt-CardAdPrice-cash']/div/div/h3")
        mData = el.get_attribute('textContent')
        index = 0
        for x in mData:
            index = index + 1
            if (x < '0' or x > '9') and x != '.':
                break
        mData = mData[0:index]
        data['price'] = int(mData.replace('.',''))
    except:
        pass

    try:
        el = driver.find_element(By.XPATH, "//p[contains(text(), 'Consumo medio')]/../p[2]")
        mData = float(el.get_attribute('textContent').split(' ')[0])
        data['consumption'] = mData
    except:
        pass

def select_car(element):
    link = element.get_attribute('href')
    driver.execute_script(f'window.open("{link}","_blank");')
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[1])
    raw_data = get_car_raw_data()
    classified_data = get_classified_data()
    time.sleep(2)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(2)
    return Car(raw_data, None)


cars = []
main_window = driver.current_window_handle
cars_items = driver.find_elements(By.CSS_SELECTOR, 'div > div.sui-AtomCard.sui-AtomCard--responsive > div.sui-AtomCard-info > a')

for car_item in cars_items:
    car = select_car(car_item)
    cars.append(car)




driver.close()