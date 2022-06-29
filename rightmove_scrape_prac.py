# import the necessary libraries
from bs4 import BeautifulSoup
import requests
import json
import re

# this function handles the situation when the html is embedded within javascript
def javascript_html_parse(source_arg):
	"""Return the JSON object as a dictionary"""
	start = "<script>window.__PRELOADED_STATE__ = "
	end = "</script"
	x = source_arg[source_arg.find(start)+len(start):]
	x = x[:x.find(end)]
	x = json.loads(x)
	return x

# while loop that obtains the address, property type, last sold price, last sold date, and its url (if it has one) from each house. 
# Stores each value into a list. This is from the web page which shows different houses from a particular area. 

page_number = 1
addresses, property_type, last_sold_price, last_sold_date, url = [], [], [], [], []
bush_hill_url = "https://www.rightmove.co.uk/house-prices/bush-hill-park.html"
# obtain the number of pages
source = requests.get("https://www.rightmove.co.uk/house-prices/bush-hill-park.html").text
a = javascript_html_parse(source)
num_pages = a["pagination"]["last"]
houses = {}
while page_number <= num_pages:

	if page_number == 1:
		source = requests.get(bush_hill_url).text
	else:
		source = requests.get(bush_hill_url+f"?page={page_number}").text

	# all we want to extract is the address, the price & date, and the URL 
	x = javascript_html_parse(source)
	for house in x["results"]["properties"]:
		addresses.append(house["address"])
		property_type.append(house["propertyType"])
		last_sold_price.append(house["transactions"][0]["displayPrice"])
		last_sold_date.append(house["transactions"][0]["dateSold"])
		url.append(house["detailUrl"])




	page_number += 1


# Create a dictionary with all of the scraped info stored in it so far
houses = {}
for i in range(len(addresses)):
	houses[addresses[i]] = [property_type[i], last_sold_price[i], last_sold_date[i], url[i]]



############################# THIS CODE EXTRACTS THE BULLET POINTED FEATURES OF EACH HOUSE - into a list ###########################
############################### Also done this down below as there was a list already in the json object (javascript)
# This is from the web pages dedicated to one particular house. 

source = requests.get("https://www.rightmove.co.uk/house-prices/details/england-113786462-92971722#/").text
soup = BeautifulSoup(source, 'lxml')

#We're first looking to extract the bullet pointed features 
key_features = str(soup.find("ul", class_="keyFeatures"))

# This code puts the bullet point features of one house into a list
a = key_features.split("<li>")[1:]
features = []
for feature in a:
	features.append(feature[:-5])
features[-1] = features[-1][:-5]
print(features) 
########################################################################################################################


####################################################################################################
# This code extracts all of the relevant information from the webpage of a sold house ###########
script = soup.find("script", {"type":"text/javascript"}).text
# Regex used to convert the JSON data structure into a python dict 
# Use regex to extract json data from the script text
json_script=re.findall(("(?s)(?<=window.PAGE_MODEL = )(.*$)"), script)[0]
# Transforming json data within string into dictionary
json_dict=json.loads(json_script)
# We managed to succesfully extract json data into a Python dict
#print(json_dict)
# Now we can work through it

# got the bullet pointed features # 
features = json_dict["soldPropertyData"]["property"]["keyFeatures"]
# got the floorplan URL
floorplan_url = json_dict["soldPropertyData"]["property"]["floorplans"][0]['url']

# Scrape the pictures of the house
house_image_urls = []
for image in json_dict["soldPropertyData"]["property"]["images"]:
	house_image_urls.append(image['url'])

# location of the house
latitude = json_dict["soldPropertyData"]["property"]["location"]["latitude"]
longitude = json_dict["soldPropertyData"]["property"]["location"]["longitude"]

# proximity to the stations
station_names, distances = [], []
for station in json_dict["soldPropertyData"]["property"]["nearestStations"]:
	station_names.append(station["name"])
	distances.append(station["distance"])
station_proximities = {station:distance for station, distance in zip(station_names, distances)}


# size of the property
units, sizes = [], []
for i in json_dict["soldPropertyData"]["property"]["sizings"]:
	units.append(i['unit'])
	sizes.append(i['maximumSize'])
dimensions = {unit:size for unit, size in zip(units, sizes)}

# number of bedrooms and bathrooms
bedrooms = json_dict["soldPropertyData"]["property"]['bedrooms']
bathrooms = json_dict["soldPropertyData"]["property"]['bathrooms']

# property type
property_type = json_dict["soldPropertyData"]["property"]['propertySubType']

# new build, price in correct format, and 
new_build = json_dict["soldPropertyData"]["transactions"][0]['newBuild']
price = json_dict["soldPropertyData"]["transactions"][0]['price']
yy_mm_dd = json_dict["soldPropertyData"]["transactions"][0]['deedDate']


# Now I want to need to add more of the 




#### This code down here is irrelevant #####

# code from the above function
# start_l = '<script type="text/javascript">    window.PAGE_MODEL = '
# end_l = '</script>'


# def javascript_html(source, start, end):
# 	b = source[source.find(start)+len(start):]
# 	b = b[:b.find(end)]
# 	b = json.loads(b)
# 	return b

# c = javascript_html(script, start_l, end_l)
# print(c)

