import os
import re
from bs4 import BeautifulSoup



regex_date = r"data-hook=\"review-date\" class=\"a-size-base a-color-secondary review-date\">(.[^<]+)"
regex_body = r"review-text-content\"><span class=\"\">(.+)</span>"
regex_title = r"ASIN=[A-Z|0-9]+\"><span class=\"\">(.+)</span>"
regex_stars = r"review-rating\"><span class=\"a-icon-alt\">([^<]+)</span></i></a><span class=\"a-letter-space\">"
regex_accountName = r"<div class=\"a-profile-content\"><span class=\"a-profile-name\">(.+)</span></div></a></div><div class=\"a-row\"><a class=\"a-link-normal\" title=\""
regex_verifiedPurchase = r"<span data-hook=\"avp-badge\" class=\"a-size-mini a-color-state a-text-bold\">(Verified Purchase)</span>"
id_regex = r"id=\"([A-Z0-9]+)\" data-hook"
def extractFromSingleFileBS4(parentFolder, fileName):
    with open(os.path.join(parentFolder,fileName),'r') as f:
        html_doc = f.read()
    divids = re.findall(id_regex, html_doc)
    print(len(divids))
    soup = BeautifulSoup(html_doc, 'html.parser')
    for divid in divids:
        print(soup.find(id=divid))

    

    
def extractFromSingleFile(parentFolder,fileName):
    with open(os.path.join(parentFolder,fileName),'r') as f:
        html_doc = f.read()
    dates = re.findall(regex_date,html_doc)
    body = re.findall(regex_body,html_doc)
    titles = re.findall(regex_title, html_doc)
    stars = re.findall(regex_stars,html_doc)
    accountNames = re.findall(regex_accountName, html_doc)
    verifiedPurchases = re.findall(regex_verifiedPurchase, html_doc)
    print(fileName ,len(dates), len(body), len(titles), len(stars), len(accountNames), len(verifiedPurchases))

id = 'B0131RG6VK'
pathToFolder = os.path.join('amazonreviews','com',id)
fileList = os.listdir(pathToFolder)
# print(fileList)
# for fileName in fileList:
#     extractFromSingleFile(os.path.join(pathToFolder,fileName))
extractFromSingleFileBS4(pathToFolder,'1.html')

