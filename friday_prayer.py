#!/usr/local/bin/python

import requests
import urllib
import time
from bs4 import BeautifulSoup
import smtplib
import schedule
import datetime
import configparser
import os
import requests

sms_server = 'http://127.0.0.1:5000/'
dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read(dir_path+'/config.ini')
subscribers = config.get('subscription','subscribers')

prev_data = []

def send_sms(datasets):
	i=0
	prayer_time = ""
	while i< len(datasets):
		prayer_time = prayer_time+datasets[i]+": "+datasets[i+1]+"\n"
		i=i+2
	print(str(datetime.datetime.now())+" -\n"+prayer_time)
	to = subscribers.split(',')
	subject = 'Jum\'ah Time'
	body = '\n'+prayer_time
	for number in to:
		payload = {'number': number, 'subject': subject, 'body': body}
		req = requests.get(sms_server+'send-text', params=payload)
		print(str(datetime.datetime.now())+" -status: "+str(req.status_code))
    
    
    
def scrape_webpage(isFriday):
	print('*************Friday prayer Notifier*************')
	try:
		url = 'https://www.bisweb.org/'
		print(str(datetime.datetime.now())+" -"+'Requesting info to '+url)
		response = requests.get(url)
		print(str(datetime.datetime.now())+" -"+'Response received.')
		soup = BeautifulSoup(response.text, "html.parser")
		div = soup.find("div", attrs={"id":"block-43"})
		table = div.find('table')
		datasets = []
		for row in table.find_all("td"):
			dataset = unicode(row.get_text())
			datasets.append(dataset)
		global prev_data
		
		
	except:
		#send_sms(['Something went wrong in web scraping.'])
		#print 
		print(str(datetime.datetime.now())+" -"+'Something went wrong in web scraping.')
		return
	if isFriday == True:
		print(str(datetime.datetime.now())+" -"+'It\'s friday.')
		prev_data = datasets
		send_sms(datasets)
		
	if len(prev_data) == 0:
		print(str(datetime.datetime.now())+" -"+'Assigning initial dataset')
		prev_data = datasets
		send_sms(datasets)
		
	elif set(prev_data) != set(datasets):
		print(str(datetime.datetime.now())+" -"+'Schedule changed')
		prev_data = datasets
		send_sms(datasets)




def main():

	print(str(datetime.datetime.now())+" -"+'Friday prayer notifier is running')
	scrape_webpage(False)

	schedule.every(4).hours.do(scrape_webpage, False)
	schedule.every().friday.at("10:00").do(scrape_webpage, True)
	print(str(datetime.datetime.now())+" -"+'Scheduled at Friday 10 AM')
	while True:
    		schedule.run_pending()
    		time.sleep(10)

		

if __name__ == "__main__": main()


