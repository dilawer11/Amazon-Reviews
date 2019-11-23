import requests
import os
import sys
import time
from bs4 import BeautifulSoup
import csv
USER_AGENT = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.91 Chrome/12.0.742.91 Safari/534.30'
urlPart1 = "http://www.amazon.com/product-reviews/"
urlPart2 = "/?ie=UTF8&showViewpoints=0&pageNumber="
urlPart3 = "&sortBy=recent"
MAX_PAGE = 100
MAX_RETRY = 10
CATEGORY_DIR_NAME = "Categories"
REVIEW_DIR_NAME = "Reviews"

CSV_FILE = None
CSV_WRITER = None
def openCSVFile(productCategory):
    global CSV_FILE
    if not os.path.isdir(REVIEW_DIR_NAME):
        os.mkdir(REVIEW_DIR_NAME)
    CSV_FILE= open(os.path.join(REVIEW_DIR_NAME, productCategory) + '.csv', 'w+')
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
    links = reviewList[0].find_all('div')
    print("Link Length", len(links))
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
            writeToCSV(productID, productCategory, productName, name, rating, date, vp, body, title)
            print()

def downloadReviewsOnePage(page, productID, productCategory, productName):
    sleepTime = 5
    for _ in range(0, MAX_RETRY):
        time.sleep(sleepTime)
        referer = urlPart1 + productID + urlPart2 + "1" + urlPart3
        url = urlPart1 + productID + urlPart2 + page + urlPart3
        r = requests.get(url ,headers={'User-Agent': USER_AGENT, 'Referrer' : referer})
        print('Page:', page, 'StatusCode:', r.status_code)
        if r.status_code == '503':
            sleepTime = sleepTime + 5
            continue
        else:                
            parsePage(r.text, productID, productCategory, productName)
        return

def scrapeOneProductID(productID, productCategory):
    mainPageURL = 'https://www.amazon.com/dp/' + productID
    mainPageResult = requests.get(mainPageURL, headers = {'User-Agent' : USER_AGENT, 'Referrer' : 'https://amazon.com'})
    soup = BeautifulSoup(mainPageResult.text, "lxml")
    productName = soup.select('#productTitle')[0].text.strip()
    for i in range (1, MAX_PAGE):
        downloadReviewsOnePage(str(i), productID, productCategory, productName)
    
def main():
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