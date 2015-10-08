#!/usr/bin/env python

#----------------------------------------#
# Output all the names from case records #
# 										 #
# This will help narrow down your search #
# to the specific individual, by looking #
# at middle initials as well as first &  #
# last name. 							 #
#										 #
# Author: Brian Warehime				 #
# nullsecure.org						 #
#----------------------------------------#

import requests
from bs4 import BeautifulSoup
from MaltegoTransform import *
import urllib as ul

# Configuration
host = "http://casesearch.courts.state.md.us"
uri = "/casesearch/processDisclaimer.jis"
data = {'disclaimer':'Y','action':'Continue'}
s = requests.Session()
me = MaltegoTransform()
me.parseArguments(sys.argv)
name = sys.argv[1]
firstname = name.split(" ")[0]
lastname = name.split(" ")[1]

# Set up session/cookies
s.get(host+uri)
s.post(host+uri, data=data)

newuri = "/casesearch/inquirySearch.jis"
newdata = "lastName="+lastname+"&firstName="+firstname+"&middleName=&partyType=&site=00&courtSystem=B&countyName=&filingStart=&filingEnd=&filingDate=&company=N&action=Search"
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
x = s.post(host+newuri, data=newdata, headers=headers)

record = x.text

soup = BeautifulSoup(record)

cases = []
rows = soup.find_all('a')
for row in rows:
	if row.has_attr('href'):
		if "inquiryDetail.jis" in row['href']:
			cases.append(row['href'].split("?")[1])

detailuri = "/casesearch/inquiryDetail.jis?"
for case in cases:
	getcase = s.get(host+detailuri+case)

	record = getcase.text
	soup = BeautifulSoup(record)

	rows = soup.find_all('tr')
	recs = []
	for row in rows:
		cols = row.find_all('td')
		cols = [ele.text.strip() for ele in cols]
		recs.append(cols)
	newlist = []

	for i in recs:
		newlist.append(",".join(i))

	finallist = []
	for c in newlist:
		if "Defendant Name" in c:
			finallist.append(str(c))

	# Format Case ID for passing it as an additional field
	newcaseid = ul.quote(case)
	for entry in finallist:
		if "Defendant Name" in entry:
			if entry.split(":")[1][0] == ",":
				newname = entry.split(":")[1][1:]	
			else:
				newname = entry.split(":")[1]
			ent = me.addEntity("maltego.Person",str(newname))
			ent.addAdditionalFields(fieldName=newcaseid,
	                            displayName=newcaseid,
	                            value=newcaseid)
me.returnOutput()