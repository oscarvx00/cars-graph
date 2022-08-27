from multiprocessing.spawn import import_main_path
import time
from tokenize import Number
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import yaml
from yaml.loader import SafeLoader
from selenium.webdriver.support import expected_conditions as EC
import json
import csv
from os.path import exists
import argparse

MAX_ADS_PAGE = int(35/4) + 1

parser = argparse.ArgumentParser(description='Coches.net data scrapper')
parser.add_argument('--pages', type=int, required=True, help='pages to explore')
parser.add_argument('--output', type=str, required=True, help='output csv filepath')

args = parser.parse_args()

def get_provinces(filepath):
    mData = []
    with open(filepath) as file:
        data = json.load(file)
        for item in data:
            mData.append(item['fields']['provincia'])
    return mData

csv_headers = [
    "brand",
    "year",
    "kms",
    "city",
    "seats",
    "power",
    "transmission",
    "fuel",
    "doors",
    "seats",
    "consumption",
    "acceleration",
    "max_speed",
    "price",
    "url"
]

class Car:
    brand = None
    year = None
    kms = None
    city = None
    seats = None
    power = None
    transmission = None
    fuel = None
    doors = None
    seats = None
    consumption = None
    acceleration = None
    max_speed = None
    price = None
    url = None

    def __init__(self, raw_data, classified_data):
        for item in raw_data:
            if item.endswith('Puertas'):
                self.doors = int(item.split(' ')[0])
            elif item.endswith('Plazas'):
                self.seats = int(item.split(' ')[0])
            elif item.endswith('km') and not item.endswith('/km'):
                self.kms = int(item.split(' ')[0].replace('.', ''))
            elif item.endswith('cv'):
                self.power = int(item.split(' ')[0])
            elif not item.endswith('cc') and item >= '1990' and item <= '2023':
                self.year = int(item)
            elif item in ['Diesel', 'Gasolina']:
                self.fuel = item
            elif item in provinces_array:
                self.city = item
            elif item.startswith('Cambio'):
                self.transmission = item.split(' ')[1]
        
        self.brand = classified_data.get('brand', None)
        self.price = classified_data.get('price', None)
        self.consumption = classified_data.get('consumption', None)
        self.acceleration = classified_data.get('acceleration', None)
        self.max_speed = classified_data.get('max_speed', None)
        self.url = classified_data.get('url', None)

    def to_csv(self):
        buff = []
        d = self.__dict__
        for key in csv_headers:
            data = d.get(key, '')
            #if data == None:
            #    data = '-'
            buff.append(data)
        return buff


with open('values.yaml') as f:
    values = yaml.load(f, Loader=SafeLoader)
    print(values)

provinces_array = get_provinces('provincias-espanolas.json')
 
options = Options()
opt = uc.ChromeOptions()
opt.add_argument('--disable-popup-blocking')
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
        el = driver.find_element(By.XPATH, "//h1[contains(@class, 'mt-TitleBasic-title')]")
        mData = el.get_attribute('textContent')
        data['brand'] = mData.split(' ')[0]
    except:
        pass

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

    try:
        el = driver.find_element(By.XPATH, "//p[contains(text(), 'Aceleración')]/../p[2]")
        mData = float(el.get_attribute('textContent').split(' ')[0])
        data['acceleration'] = mData
    except:
        pass
    
    try:
        el = driver.find_element(By.XPATH, "//p[contains(text(), 'Velocidad')]/../p[2]")
        mData = float(el.get_attribute('textContent').split(' ')[0])
        data['max_speed'] = mData
    except:
        pass

    data['url'] = driver.current_url

    return data


def select_car(link):
    
    driver.execute_script(f'window.open("{link}","_blank");')
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[1])
    raw_data = get_car_raw_data()
    classified_data = get_classified_data()
    time.sleep(2)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(2)
    return Car(raw_data, classified_data)

def get_ad_height():
    element = driver.find_element(By.CSS_SELECTOR, 'div.mt-App > main > div.mt-AdsList-inner > section > div.mt-ListAds > div:nth-child(1)')
    return element.size['height']

def get_car_links(item_height):
    links_set = set()

    for x in range(MAX_ADS_PAGE):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, 'div > div.sui-AtomCard.sui-AtomCard--responsive > div.sui-AtomCard-info > a')
            for el in elements:
                link = el.get_attribute('href')
                links_set.add(link)
                driver.execute_script(f'window.scrollBy(0, {item_height+20});')
        except:
            pass

    return list(links_set)


def save_to_csv(headers, data, filepath):
    if not exists(filepath):
        with open(filepath, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data)
    else:
        with open(filepath, 'a+', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(data)

    

try:
    cars_links = []
    for y in range(args.pages):     
        cars = []
        main_window = driver.current_window_handle 
        #cars_links = driver.find_elements(By.CSS_SELECTOR, 'div > div.sui-AtomCard.sui-AtomCard--responsive > div.sui-AtomCard-info > a')
        cars_links = cars_links + get_car_links(get_ad_height())
        driver.find_element(By.XPATH, "//li[a/span/span[text()='Siguiente']]").click()
        
    print("Detected %d cars"%len(cars_links))
    index = 0
    for car_link in cars_links:
            car = select_car(car_link)
            cars.append(car)
            index = index + 1
            print("--> %d of %d"%(index, len(cars_links)))
        
except:
    pass


cars_csv = []
for c in cars:
    cars_csv.append(c.to_csv())
    
save_to_csv(csv_headers, cars_csv, args.output)


driver.close()