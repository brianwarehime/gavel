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
import re

# Configuration
host = "http://casesearch.courts.state.md.us"
uri = "/casesearch/processDisclaimer.jis"
data = {'disclaimer':'Y','action':'Continue'}
s = requests.Session()
me = MaltegoTransform()
me.parseArguments(sys.argv)
cases = me.getVars()
oldname = sys.argv[1]
# Set up session/cookies
s.get(host+uri)
s.post(host+uri, data=data)

unquotedcases = []
for case in cases:
	case = ul.unquote(case)
	if "caseId" in case:
		unquotedcases.append(case)
	else:
		pass

detailuri = "/casesearch/inquiryDetail.jis?"
for case in unquotedcases:
	getcase = s.get(host+detailuri+case)

	record = getcase.text
	soup = BeautifulSoup(record)
	if soup.findAll(text = re.compile('Vehicle')):
		rows = soup.find_all('tr')
		recs = []
		for row in rows:
			cols = row.find_all('td')
			cols = [ele.text.strip() for ele in cols]
			recs.append(cols)
		newlist = []

		for i in recs:
			newlist.append(",".join(i))

		addresslist = []
		vehiclelist = []
		personmeta = []
		datemeta = []
		for c in newlist:
			if "Address" in c:
				addresslist.append(str(c))
			elif "City" in c:
				addresslist.append(str(c))
			elif "Vehicle" in c:
				vehiclelist.append(str(c))
			elif "Sex" in c:
				personmeta.append(str(c))
			elif "DOB" in c:
				datemeta.append(str(c))

		# Format Case ID for passing it as an additional field
		newcaseid = ul.quote(case)
		
		ent = me.addEntity("maltego.Location",str(addresslist[0].split(":")[1])+"\n"+addresslist[1].split(":")[1].split("State")[0].strip(",")+", "+
			addresslist[1].split("State:")[1].split("Zip Code:")[0]+" "+
			addresslist[1].split("Zip Code:")[1])
		ent.addAdditionalFields(fieldName="streetaddress",
		                        displayName="streetaddress",
		                        value=addresslist[0].split(":")[1])
		
		oldent = me.addEntity("maltego.Person",oldname)
		oldent.addAdditionalFields(fieldName="Height",
								displayName="Height",
								value=personmeta[0].split("Height:")[1].split("Weight")[0])
		oldent.addAdditionalFields(fieldName="Weight",
								displayName="Weight",
								value=personmeta[0].split("Weight:")[1])
		oldent.addAdditionalFields(fieldName="DOB",
								displayName="DOB",
								value=datemeta[0].split(":")[1])

		newent = me.addEntity("maltego.Car",str(vehiclelist[0].split(",")[1].split(",")[0]))
		newent.addAdditionalFields(fieldName="Make",
		                        displayName="Make",
		                        value=vehiclelist[0].split("Description:,")[1])
	else:
		pass
	
me.returnOutput()