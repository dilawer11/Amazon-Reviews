from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.proxy import Proxy, ProxyType
import os
import re
import time
final_urls = []
URL_FILE = "url_categories.txt"
REGEX_PRODUCTID = r"dp/([^\/]+)"
MAX_NEXT_PAGE = 100
productSelector = '#search > div.sg-row > div.sg-col-20-of-24.sg-col-28-of-32.sg-col-16-of-20.sg-col.s-right-column.sg-col-32-of-36.sg-col-8-of-12.sg-col-12-of-16.sg-col-24-of-28 > div > span:nth-child(5) > div.s-result-list.s-search-results.sg-row > div > div > span > div > div > div:nth-child(2) > div:nth-child(1) > div > div > span > a'
categorySelector = '#search > span.rush-component > h1 > div > div.sg-col-14-of-20.sg-col-26-of-32.sg-col-18-of-24.sg-col.sg-col-22-of-28.s-breadcrumb.sg-col-10-of-16.sg-col-30-of-36.sg-col-6-of-12 > div > div > span.a-color-state.a-text-bold'
CATEGORY_DIR_NAME = 'Categories'
driver = webdriver.Chrome()
def writeToCategoryFile(productIDs, category):
    if not os.path.isdir(CATEGORY_DIR_NAME):
        os.mkdir(CATEGORY_DIR_NAME)
    fileName = os.path.join(CATEGORY_DIR_NAME,category + '.txt')
    try:
        with open(fileName, 'r') as f:
            existingIDs = f.read().split('\n')
        with open(fileName, 'a+') as f:
            for productID in productIDs:
                if productID not in existingIDs:
                    f.write(productID + '\n')
    except:
        with open(fileName, 'w+') as f:
            for productID in productIDs:
                f.write(productID + '\n')
 

def scrapeOnePage(url):
    for _ in range(0,3):
        driver.get(url)
        try:
            category = driver.find_element(By.CSS_SELECTOR, categorySelector)
            print(category.get_attribute('innerHTML'))
        except:
            print("Failed Trying Again")
            continue
        try:
            products = driver.find_elements(By.CSS_SELECTOR, productSelector)
        except:
            print('Failed Trying Again')
            continue
        for product in products:
            final_urls.append(product.get_attribute('href'))
        productIDs = list(map(lambda x : re.findall(REGEX_PRODUCTID, x)[0], final_urls))
        writeToCategoryFile(productIDs, category.get_attribute('innerHTML'))

        return

def scrapeMultiPage(initialURL):
    scrapeOnePage(initialURL)
    for i in range(1, MAX_NEXT_PAGE):
        time.sleep(5)
        scrapeOnePage(initialURL + '&page=' + str(i))
def main():
    with open(URL_FILE, 'r') as f:
        urls = f.read().split('\n')
    for url in urls:
        scrapeMultiPage(url)

if __name__ == "__main__":
     main()

