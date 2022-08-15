import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
import yaml
from yaml.loader import SafeLoader



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

ad_index = 1
while True:
    try:
        #element = driver.find_element(By.XPATH, f"//div[contains(@class, 'mt-ListAds-item')][{ad_index}]")
        element = driver.find_element(By.CSS_SELECTOR, 'div.mt-ListAds')
    except:
        print('')
#//div[contains(@class, 'mt-ListAds-item')][1]
 
#def apply_filter():


driver.close()