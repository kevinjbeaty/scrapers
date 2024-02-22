import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
SLACKURL = os.environ['SLACKURL']
url = 'https://www.journalismjobs.com/job-listings?keywords=&location=0&jobType=&date=&industries=0%2C1%2C5%2C3%2C4%2C13%2C7%2C8%2C14%2C12%2C6%2C10%2C15%2C11&position=&diversity=&focuses=&salary=&company=&title=&virtual=&page=1&count=25'
data = requests.get(url).text
soup = BeautifulSoup(data, 'html.parser')
listings = soup.find_all('div',{'class':'main'})[0].find_all('a')
now = datetime.now()
for i in listings:
    if (str(now.strftime('%B')) + ' ' + str(now.day)) in i.text:
        company = i.find('div',{'class':'job-item-company'}).text
        title = i.find('h3',{'class':'job-item-title'}).text
        location = i.find_all('i')[0].parent.text.replace(' ','').replace('\n','')
        postThis = {'text':'<https://example.com|' + company + ' -- ' + title + ' -- ' + location + '>'} 
        response = requests.post(SLACKURL, data=json.dumps(postThis), headers={'Content-Type': 'application/json'})        
