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

# Obtain all of the URL's that need to be scraped from 
# This is the first URL we start at, here we are collecting all of the URL's to be scraped from into 
# local area URL's 
url = "https://www.rightmove.co.uk/house-prices-in-London.html"
source = requests.get(url).text
soup = BeautifulSoup(source, 'lxml')
b = soup.find_all("a", class_="head")
london_urls = []
for i in b:
	london_urls.append(i["href"])

borough_urls = []
for url in london_urls:
	source = requests.get(url).text
	soup = BeautifulSoup(source, 'lxml')
	b = soup.find_all("a", class_="head")
	for i in b:
		borough_urls.append(i["href"])

local_area_urls = []
for url in borough_urls:
	source = requests.get(url).text
	soup = BeautifulSoup(source, 'lxml')
	b = soup.find_all("a", class_="head")
	for i in b:
		local_area_urls.append(i["href"])	

# iterate over all of the URL's and scrape from them, and store the scraped data into a variable called houses
houses = {}
for area_url in local_area_urls[:5]:

	# while loop that obtains the address, property type, last sold price, last sold date, and its url (if it has one) from each house. 
	# Stores each value into a list. This is from the web page which shows different houses from a particular area.

	page_number = 1
	addresses, property_type, last_sold_price, last_sold_date, url = [], [], [], [], []
	#bush_hill_url = "https://www.rightmove.co.uk/house-prices/bush-hill-park.html"
	# obtain the number of pages to use in the while loop condition
	source = requests.get(area_url).text
	a = javascript_html_parse(source)
	num_pages = a["pagination"]["last"]
	#houses = {}
	while page_number <= num_pages:

		if page_number == 1:
			source = requests.get(area_url).text
		else:
			source = requests.get(area_url+f"?page={page_number}").text

		# all we want to extract is the address, the price & date of the last sale, and the URL.
		x = javascript_html_parse(source)
		for house in x["results"]["properties"]:
			addresses.append(house["address"])
			property_type.append(house["propertyType"])
			last_sold_price.append(house["transactions"][0]["displayPrice"])
			last_sold_date.append(house["transactions"][0]["dateSold"])
			url.append(house["detailUrl"])



		page_number += 1


	# Create a dictionary with all of the scraped info stored in it so far
	#houses = {}
	for i in range(len(addresses)):
		houses[addresses[i]] = {"property_type":property_type[i], "price":last_sold_price[i], "date":last_sold_date[i], "url": url[i]}




	for v in houses.values():
		if v['url'] == '':
			continue
		else:
			source = requests.get(v['url']).text
			soup = BeautifulSoup(source, 'lxml')
			script = soup.find("script", {"type":"text/javascript"}).text
			# Regex used to convert the JSON data structure into a python dict 
			# Use regex to extract json data from the script text
			json_script=re.findall(("(?s)(?<=window.PAGE_MODEL = )(.*$)"), script)[0]
			# Transforming json data within string into dictionary
			json_dict=json.loads(json_script)

			# The bullet pointed features # 
			try:
				features = json_dict["soldPropertyData"]["property"]["keyFeatures"]
			except TypeError: 
				pass
			else:
				v["features"] = features
			# got the floorplan URL
			try:
				floorplan_url = json_dict["soldPropertyData"]["property"]["floorplans"][0]['url']
			except Exception:
				# seen a TypeError and an IndexError
				pass
			else:
				v["floorplan_url"] = floorplan_url	
			# Scrape the pictures of the house
			house_image_urls = []
			for image in json_dict["soldPropertyData"]["property"]["images"]:
				house_image_urls.append(image['url'])
			v["house_image_urls"] = house_image_urls
			# location of the house
			latitude = json_dict["soldPropertyData"]["property"]["location"]["latitude"]
			longitude = json_dict["soldPropertyData"]["property"]["location"]["longitude"]
			v["latitude"] = latitude
			v["longitude"] = longitude
			# proximity to the stations
			station_names, distances = [], []
			for station in json_dict["soldPropertyData"]["property"]["nearestStations"]:
				station_names.append(station["name"])
				distances.append(station["distance"])
			station_proximities = {station:distance for station, distance in zip(station_names, distances)}
			v["station_proximities"] = station_proximities
			# size of the property
			units, sizes = [], []
			for i in json_dict["soldPropertyData"]["property"]["sizings"]:
				units.append(i['unit'])
				sizes.append(i['maximumSize'])
			dimensions = {unit:size for unit, size in zip(units, sizes)}
			v["property_size"] = dimensions

			# number of bedrooms and bathrooms
			bedrooms = json_dict["soldPropertyData"]["property"]['bedrooms']
			bathrooms = json_dict["soldPropertyData"]["property"]['bathrooms']
			v["bedrooms"] = bedrooms
			v["bathrooms"] = bathrooms

			# Whether the property is a new build or not
			new_build = json_dict["soldPropertyData"]["transactions"][0]['newBuild']
			v["new_build"] = new_build



print()
print(houses)










# Now I want to add all of this information for a single house stored in a dictionary 

#scraped_houses = []
#house_dict = {}
#[{29 bell lane: {price:82,000,
#				   date: 26/02/2022}},]





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

