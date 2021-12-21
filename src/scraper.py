from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

s=Service('../resources/chromedriver')
driver = webdriver.Chrome(service=s)
driver.get("https://www.thetrainline.com")

def scrape_for_cheapets_ticket():
    return None

