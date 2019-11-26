import requests
import os
import sys
import time
from bs4 import BeautifulSoup
import csv
import random
from proxy import getProxiesHTTP, getProxiesHTTPS
import threading
PROXYLISTHTTP = []
PROXYLISTHTTPS = []
USER_AGENT = [  
                'Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.91 Chrome/12.0.742.91 Safari/534.30',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'
            ]
urlPart1 = "http://www.amazon.com/product-reviews/"
urlPart2 = "/?ie=UTF8&showViewpoints=0&pageNumber="
urlPart3 = "&sortBy=recent"
MAX_PAGE = 100
MAX_RETRY = 1000
MONTHS = ["August", "November", "September", "October"]
MIN_YEAR = 2019
CATEGORY_DIR_NAME = "Categories"
REVIEW_DIR_NAME = "Reviews"
CSV_FILE = None
CSV_WRITER = None
PROXY_FILE = 'proxy.txt'
LASTREQUESTTIME = 0
def loadProxies():
    while(1):
        print('Updating Proxies')
        global PROXYLISTHTTP
        global PROXTLISTHTTPS
        PROXYLISTHTTP = getProxiesHTTP()
        PROXYLISTHTTPS = getProxiesHTTPS()
        print('Updates Proxies : HTTP=' + str(len(PROXYLISTHTTP)) + ' ' + 'HTTPS=' + str(len(PROXTLISTHTTPS)))
        time.sleep(300) #Sleep for 5 minutes
def openCSVFile(productCategory):
    global CSV_FILE
    if not os.path.isdir(REVIEW_DIR_NAME):
        os.mkdir(REVIEW_DIR_NAME)
    CSV_FILE= open(os.path.join(REVIEW_DIR_NAME, productCategory) + '.csv', 'a+')
    global CSV_WRITER
    CSV_WRITER = csv.writer(CSV_FILE, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    
def writeToCSV(productID, productCategory, productName, name, rating, date, verifiedPurchase, body, title):
    if verifiedPurchase == "Verified Purchase":
        vp = "Yes"
    else:
        vp = "No"
    CSV_WRITER.writerow([productID, productCategory, productName, name, date, vp, rating, title, body])

def parsePage(fileData, productID, productCategory, productName):
    
    soup = BeautifulSoup(fileData, "lxml")
    reviewList = soup.select('#cm_cr-review_list')
    print("Length", len(reviewList))
    if len(reviewList) == 0:
        with open('error.html' , 'w+') as f:
            f.write(fileData)
        return "Error"
    links = reviewList[0].find_all('div')
    print("Link Length", len(links))
    if len(links) < 2:
        return "Error"
    elif len(links) == 2:
        return "DateExceeded"
    for card in links:
        if(card.get('data-hook') == 'review'):
            name = ""
            rating = ""
            date = ""
            title = ""
            body = ""
            vp = ""
            for link in card.find_all('a'):
                if(link.get('data-hook') == 'review-title'):
                    print('Title:   ', link.text.strip())
                    title = link.text.strip()
            for span in card.find_all('span'):
                if(span.get('class') and span.get('class')[0] == 'a-profile-name'):
                    print('Name:    ', span.text)
                    name = span.text
                elif(span.get('data-hook') == 'review-date'):
                    print('Date:    ', span.text)
                    date = span.text
                elif(span.get('data-hook') == 'review-body'):
                    print('Body:    ', span.text.strip())
                    body = span.text.strip()
                elif(span.get('data-hook') == 'avp-badge'):
                    print('VP:      ', span.text)
                    vp = span.text
                elif(span.get('class') and span.get('class')[0] == 'a-icon-alt'):
                    print('Rating:  ', span.text)
                    rating = span.text
            if int(date.split(' ')[2]) < MIN_YEAR:
                return "DateExceeded"
            elif date.split(' ')[0] not in MONTHS:
                return "DateExceeded"
            writeToCSV(productID, productCategory, productName, name, rating, date, vp, body, title)
            print()
    return "Done"

def downloadReviewsOnePage(page, productID, productCategory, productName):
    sleepTime = 5
    choiceArray = [0,0,1]
    for j in range(0, MAX_RETRY):
        loadProxies()
        time.sleep(sleepTime)
        referer = urlPart1 + productID + urlPart2 + "1" + urlPart3
        url = urlPart1 + productID + urlPart2 + page + urlPart3
        proxies = {
            "http": random.choice(PROXYLISTHTTP),
            "https": random.choice(PROXYLISTHTTPS)
        }
        try:
            i = random.choice(choiceArray)
            if i == 0 or j < 5:
                r = requests.get(url ,headers={'User-Agent': random.choice(USER_AGENT), 'Referrer' : referer})
            else:
                r = requests.get(url ,headers={'User-Agent': random.choice(USER_AGENT), 'Referrer' : referer}, proxies=proxies)
        except Exception as e:
            if i == 0 or j < 5:
                sleepTime = sleepTime + 10
            else:
                sleepTime = min(120,sleepTime)
            print('Failed Request')
            print(e)
            continue
        print('Page:', page, 'StatusCode:', r.status_code)
        if r.status_code == '503':
            sleepTime = sleepTime + 5
            continue
        else:                
            resp = parsePage(r.text, productID, productCategory, productName)
            if resp == "Error":
                sleepTime = 30
                print("Error")
            else:
                return resp

def scrapeOneProductID(productID, productCategory):
    while(1):
        mainPageURL = 'https://www.amazon.com/dp/' + productID
        try:
            mainPageResult = requests.get(mainPageURL, headers = {'User-Agent' : random.choice(USER_AGENT), 'Referrer' : 'https://amazon.com'})
        except Exception as e:
            print("Failed")
            print(e)
            continue
        try:
            soup = BeautifulSoup(mainPageResult.text, "lxml")
            productName = soup.select('#productTitle')[0].text.strip()
            print("Request Succeded")
        except:
            with open('error.html','w+') as f:
                f.write(mainPageResult.text)
            time.sleep(30)
            continue
        for i in range (1, MAX_PAGE):
            res = downloadReviewsOnePage(str(i), productID, productCategory, productName)
            if res == "DateExceeded":
                return
        return
    
def main():
    threading.Thread(target=loadProxies).start()
    categoryList = list(map(lambda x: x.split('.')[0], os.listdir(CATEGORY_DIR_NAME)))
    for category in categoryList:
        openCSVFile(category)
        with open(os.path.join(CATEGORY_DIR_NAME,category + '.txt'), 'r') as f:
            productIDList = f.read().split('\n')
        for productID in productIDList:
            scrapeOneProductID(productID, category)
        CSV_FILE.close()



# if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         print("Error Enter Product ID and Category")
#     else:
#         global PRODUCT_ID
#         global PRODUCT_CATEGORY
#         PRODUCT_ID = sys.argv[1]
#         PRODUCT_CATEGORY = sys.argv[2]
#         main()
if __name__ == "__main__":
    main()
