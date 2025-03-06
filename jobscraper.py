import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os
SLACKURL = os.environ['SLACKURL']
url = 'https://www.journalismjobs.com/job-listings?keywords=&location=&jobType=&date=&industries=1%2C5%2C3%2C4%2C13&position=&diversity=&focuses=&salary=&company=&title=&virtual=&page=1&count=50'
data = requests.get(url).text
soup = BeautifulSoup(data, 'html.parser')
soup = soup.find('div',{'class':'main-jobs'})
listings = soup.find_all('a')
now = datetime.now()
now = now - timedelta(hours=7)
print(str(now.strftime('%B')) + ' ' + str('{:02d}'.format(now.day)))

for i in listings:
    if (str(now.strftime('%B')) + ' ' + str('{:02d}'.format(now.day))) in i.text:
        company = i..find('div',{'class':'job-item-company'}).text
        title = i.find('h3',{'class':'job-item-title'}).text
        location = i.find('ul',{'class':'job-item-details'}).find_all('li')[0].text.replace('\n','').replace('  ','')
        postThis = {'text':'<https://example.com|' + company + ' -- ' + title + ' -- ' + location + '>'} 
        response = requests.post(SLACKURL, data=json.dumps(postThis), headers={'Content-Type': 'application/json'})        
