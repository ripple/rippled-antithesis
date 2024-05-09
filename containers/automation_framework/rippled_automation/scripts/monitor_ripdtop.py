import bs4
import requests, smtplib
from requests.auth import HTTPBasicAuth
import time
from selenium import webdriver

driver = webdriver.Chrome('')
driver.get('http://www.google.com/');
time.sleep(5) # Let the user actually see something!
search_box = driver.find_element_by_name('q')
search_box.send_keys('ChromeDriver')
search_box.submit()
time.sleep(5) # Let the user actually see something!
driver.quit()


op = webdriver.ChromeOptions()
op.add_argument('headless')
driver = webdriver.Chrome(options=op)



# Download page
getPage = requests.get('https://ripdtop.ripple.com/', auth=HTTPBasicAuth('mdoshi', 'b@Bybu11et15'))
getPage.raise_for_status() #if error it will stop the program


menu = bs4.BeautifulSoup(getPage.text, 'html.parser')
foods = menu.select('.foodname')
