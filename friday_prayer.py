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

dir_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read(dir_path+'/config.ini')
gmail_user = config.get('credentials', 'user')
gmail_password = config.get('credentials', 'passwd')
subscribers = config.get('subscription','subscribers')

prev_data = []

def send_sms(datasets):
	i=0
	prayer_time = ""
	while i< len(datasets):
		prayer_time = prayer_time+datasets[i]+": "+datasets[i+1]+"\n"
		i=i+2
	print(str(datetime.datetime.now())+" -\n"+prayer_time)
	sent_from = gmail_user
	to = subscribers.split(',')
	subject = 'Jum\'ah Time'
	body = '\n'+prayer_time

	#email_text = """From: %s\nTo: %s\nSubject: %s\n\n%s\n
    	#""" % (sent_from, ", ".join(to), subject, body)
	email_text = """To: %s\nSubject: %s\n\n%s\n
    	""" % (", ".join(to), subject, body)

	try:
		print(str(datetime.datetime.now())+" -"+'Sending text...')
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.ehlo()
		server.starttls()
		server.login(gmail_user, gmail_password)
		server.sendmail(sent_from, to, email_text)
		server.close()

		print(str(datetime.datetime.now())+" -"+'Text sent: '+str(to))
	except:
		print(str(datetime.datetime.now())+" -"+'Failed to send text')

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
    except:
		send_sms(['Something went wrong in web scraping.'])
		print 
		print(str(datetime.datetime.now())+" -"+'Something went wrong in web scraping.')




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


