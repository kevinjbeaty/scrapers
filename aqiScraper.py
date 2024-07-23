# This script grabs the latest AQI data for the CAMP sensor downtown, hosted by an EPA contractor, and adds it to a Google spreadsheet.

import requests
import pandas as pd
import io
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import gspread
import os


# Let's define some basic variables

AQIKEY = os.environ['AQIKEY']
nowGMT = datetime.now()
nowMST = nowGMT - timedelta(hours=6)


# 1/3: Take the given hour (one hour behind or more, based on how long the data lags), format it and ship it for data collection.

def loadcurrenthour(timeGMT, timeMST):
    # We need to subtract one hour from both variables, since the data will never load for the current hour.
    timeGMT = timeGMT - timedelta(hours=1)
    timeMST = timeMST - timedelta(hours=1)
    hourMST = int("{:02d}".format(timeMST.hour))
    mvalue = " a.m."
    # This formats the MST hour into something usable in the graph.
    if (hourMST == 12):
        mvalue = " p.m."
    if (hourMST > 12):
        mvalue = " p.m."
        hourMST = hourMST-12
    if (hourMST == 0):
        mvalue = " a.m."
        hourMST = 12
    hourMST = str(hourMST) + mvalue
    scrapethishour(timeGMT, hourMST)

    
# 2/3: Use the time variables to pull the latest AQI data.
# The master AQI file is datelogged in GMT. We also need to pass the corresponding MST hour for use in the spreadsheet.

def scrapethishour(timeGMT, hourMST):
    # Call the AQI dataset via GMT time.
    datestring = str(timeGMT.year) + str("{:02d}".format(timeGMT.month)) + str("{:02d}".format(timeGMT.day))
    url = "https://s3-us-west-1.amazonaws.com//files.airnowtech.org/airnow/" + str(timeGMT.year) + "/" + datestring + "/HourlyAQObs_" + datestring + str("{:02d}".format(timeGMT.hour)) + ".dat"
    print(url)
    data = requests.get(url).content
    df = pd.read_csv(io.StringIO(data.decode('utf-8')))
    # Find the Denver data.
    row = df[df['AQSID'] == "080310013"]
    #080310002
    row = row.fillna(0)
    ozone = row['OZONE_AQI'].item()
    pm25 = row['PM25_AQI'].item()
    pm10 = row['PM10_AQI'].item()
    no2 = row['NO2_AQI'].item()
    currentreadings = {ozone, pm25, pm10, no2}
    # Determine AQI based on highest value of each chemical.
    maxreading = max(currentreadings)
    print(maxreading, hourMST)
    loaditin(maxreading, hourMST)

    
# 3/3: Load the most recent data into a Google spreadsheet where embeddedable charts auto-update.
    
def loaditin(maxreading, hourMST):
    gc = gspread.service_account(filename='./creds.json')
    gsheet = gc.open_by_key(AQIKEY)
    sheetdata = gsheet.get_worksheet(1)
    sheetdata.update("A2", maxreading)
    sheetdata.update("B2", hourMST)
    cumulativedata = gsheet.get_worksheet(2)
    # This bit moves old data up a row and leaves room for the new row, to keep the chart centered on the last 24 hours.
    if (cumulativedata.acell("B25").value != hourMST):
        x = range(3, 26)
        for i in x:
            oldcellA = cumulativedata.acell("A" + str(i)).value
            oldcellB = cumulativedata.acell("B" + str(i)).value
            cumulativedata.update("A" + str(i-1), oldcellA)
            cumulativedata.update("B" + str(i-1), oldcellB)
        cumulativedata.update("A25", maxreading)
        cumulativedata.update("B25", hourMST)
    if (hourMST == "12 a.m."):
        dailymax = int(cumulativedata.acell("I10").value)
        cumulativedata.update("I11", dailymax)


# This stuff kicks off the function chain, starting with the most current hour and working backwards if that fails because the data is delayed.
# I added four extra attempts in case the data is *really* late, which happens sometimes.

try:
    loadcurrenthour(nowGMT, nowMST)
except:
    try:
        loadcurrenthour(nowGMT - timedelta(hours=1), nowMST - timedelta(hours=1))
    except:
        try:
            loadcurrenthour(nowGMT - timedelta(hours=2), nowMST - timedelta(hours=2))
        except:
            try:
                loadcurrenthour(nowGMT - timedelta(hours=3), nowMST - timedelta(hours=3))
            except:
                try:
                    loadcurrenthour(nowGMT - timedelta(hours=4), nowMST - timedelta(hours=4))
                except:
                    pass
