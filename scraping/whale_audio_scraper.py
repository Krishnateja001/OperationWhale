import requests
import json
import re
import os

link = 'https://whoicf2.whoi.edu/science/B/whalesounds/WhaleSounds/9900100{c}.wav'
parent_path = "/Users/kt/Documents/personal_projects/operationWhale/test_sounds/"
def whale_audio():
    count = 0
    while(True):
        count+=1
        print(count)
        # try:
        print('save')
        response = requests.get(link.format(c=count))
        if response.status_code ==404:
            print(response.status_code)
            break
        open('/Users/kt/Documents/personal_projects/operationWhale/test_sounds/belugawhite_whale/beluga_whale_{c}.wav'.format(c=count),'wb').write(response.content)
        # except:
        #     break


from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
webpage_link ="https://whoicf2.whoi.edu/science/B/whalesounds/bestOf.cfm?code=BE3C"

def get_all_webpage_links():
    req = Request(webpage_link)
    html_page = urlopen(req)

    soup = BeautifulSoup(html_page, "lxml")

    links = []
    for link in soup.findAll('a'):
        links.append(link.get('href'))

    return links

def process_links(links):
    processed_links=[]

    for link in links:
        if re.findall(r".*.wav",link):
            processed_links.append("https://whoicf2.whoi.edu/"+link)

    return processed_links

def download_save(processed_links):
    path = parent_path+'long_finned_pilot_whale/'
    os.makedirs(path)
    for link in processed_links:
        response =requests.get(link)
        print(link)
        if response.status_code==404:
            print("link not found:",link)
        name = link.split('/')[-1:][0]
        xpath=parent_path+'long_finned_pilot_whale/{c}'.format(c=name)
        open(xpath,'wb').write(response.content)
    return None

def main():
    links = get_all_webpage_links()
    proceseed_links= process_links(links)
    download_save(proceseed_links)

main()