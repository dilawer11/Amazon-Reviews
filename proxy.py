from bs4 import BeautifulSoup
import requests
import time
proxiesHTTP = []
proxiesHTTPS = []

def getProxiesHTTP():
    requestForProxies()
    return proxiesHTTP
def getProxiesHTTPS():
    requestForProxies()
    return proxiesHTTPS
def requestForProxies():
    for _ in range(0,3):
        try:
            resp = requests.get('https://free-proxy-list.net/')
            print("Got Proxy List. Now Processing Them")
            soup = BeautifulSoup(resp.text, "lxml")
            proxyList = soup.select('#proxylisttable > tbody > tr')
            for proxy in proxyList:
                col = proxy.select('td')
                if col[6].text == "yes":
                    proxiesHTTPS.append("https://" + col[0].text + ":" + col[1].text)
                else:
                    proxiesHTTP.append("http://" + col[0].text + ":" + col[1].text)
            print('Got All Proxies')
            return
        except KeyboardInterrupt:
            exit(1)
        except Exception as e:
            print("Error", e)
            time.sleep(5)
            continue
