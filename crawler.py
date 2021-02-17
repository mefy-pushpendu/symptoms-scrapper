import sys
import requests
# from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
import re
import pymongo
from pymongo import MongoClient
import os

clear = lambda: os.system('clear')
client = MongoClient('mongodb://localhost:27017/')
db = client.diseaseDatabase

alllinks = []


def gatherlinks(letter):
    print("Gathering Links for "+letter)
    URL = 'https://www.medicinenet.com/symptoms_and_signs/alpha_'+letter+'.htm'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.findAll('li')
    end_array = re.compile(r'_a.htm">A</a>')
    start_array = re.compile(r'_z.htm">Z</a>')
    contains_https = re.compile(r'https://')
    collect = True
    repeat = False
    done = True
    for x in results:
        # push the code into the temporary array
        if collect == True and done == False:
            if str(x).split('"')[1] != "/symptoms_and_signs/alpha_a.htm" and contains_https.search(str(x)):
                alllinks.append(str(x).split('"')[1])
        if start_array.search(str(x)):
            collect = True
        if end_array.search(str(x)):
            collect = not collect
            done = not done
        else:
            print("")


alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]

for letter in alphabet:
    gatherlinks(letter)


def scrap(link):
    print(link)
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    title = str(soup.title).replace("<title>", "").replace(
        "</title>", "").split("Symptoms")[0].replace(":", "")
    description = soup.select("#ForumCenter_fmt p")[1] if soup.select(
        "#ForumCenter_fmt p") else soup.select("#pageContainer p")[0]
    symptoms = soup.select(".apPage ul li")
    single_symptom = ""
    # print(str(symptoms))
    for li in symptoms:
        single_symptom = str(li)
        single_symptom = re.sub(r'<(?:li\b[^>]*>|/li>)', "", single_symptom)
        single_symptom = re.sub(r'<(?:a\b[^>]*>|/a>)', "", single_symptom)
        single_symptom = re.sub(r',', "", single_symptom)
        if single_symptom == "A" or "<" in single_symptom:
            break
    print(single_symptom)
    strdescription = str(description)
    strdescription = re.sub(r'<(?:a\b[^>]*>|/a>)', "", strdescription)
    strdescription = re.sub(r'<(?:p\b[^>]*>|/p>)', "", strdescription)
    strdescription = re.sub(r'<(?:ul\b[^>]*>|/ul>)', "", strdescription)
    strdescription = re.sub(r'<(?:li\b[^>]*>|/li>)', "", strdescription)
    strdescription = strdescription.replace("</a>", "")
    strdescription = strdescription.replace("<p>", "")
    strdescription = strdescription.replace("</p>", "")
    # strdescription = strdescription.replace("\n","")
    print("Title : " + title)
    print("Description : " + strdescription + "\n")
    collection = db.diseases
    post_data = {
     'title': title,
     'description': strdescription,
     'symptoms': str(single_symptom)
    }
    result = collection.insert_one(post_data)
    print('One post: {0}'.format(result.inserted_id))


for link in alllinks:
    clear()
    print("Scrapping "+str(alllinks.index(link))+" of "+str(len(alllinks)))
    scrap(link)
    # break
