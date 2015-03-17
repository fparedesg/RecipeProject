from bs4 import BeautifulSoup
import urllib2
import string
import json
from random import randint
import nltk
from math import ceil

def MakeThisRegion(region,paredData,directions):
	print "\n\nLet's make a meal in this style: ", region, "\n"
	myFood = {}
	myFood["foodIngredient"]= []
	mapIndex = {}
	for i,item in enumerate(paredData):
		myFood["foodIngredient"].append(item["ingredient"])
		mapIndex[item["ingredient"]] = i
	myFood["directions"] = directions

	#this is the knowledge base for region shall be filled by process the common data of flavor and type.
	RegionproteinSet   = set()
	RegionvegetableSet = set()
	RegionherbSet      = set()
	RegionsourSet      = set()
	RegionsweetSet     = set()
	RegionbitterSet    = set()
	RegionspicySet     = set()
	RegionFlavorSet    =[RegionsourSet,RegionsweetSet,RegionbitterSet,RegionspicySet]
	RegionTypeSet      =[RegionproteinSet,RegionvegetableSet,RegionFlavorSet]

	#this is the knowledge base for the food type.
	herbKnowledgeSet = set()
	vegetableKnowledgeSet = set()
	meatKnowledgeSet = set()
	knowledgeBaseType = [meatKnowledgeSet,vegetableKnowledgeSet,herbKnowledgeSet]
	knowledgeBaseTypeFileName= ["meat","vegetable","herbs"]

	#this is the knowledge base for flavor.
	sourKnowledgeSet  = set()
	sweetKnowledgeSet = set()
	bitterKnowledgeSet= set()
	spicyKnowledgeSet = set()
	knowledgeBaseFlavor = [sourKnowledgeSet,sweetKnowledgeSet,bitterKnowledgeSet,spicyKnowledgeSet]
	knowledgeBaseFlavorFileName = ["sour","sweet","bitter","spicy"]

	#initialize the knowledgebase for Type
	for i in range(0,len(knowledgeBaseTypeFileName)):
		for j,line in enumerate(open('type/'+knowledgeBaseTypeFileName[i],'r')):
			for word in line.lower().split():
				knowledgeBaseType[i].add(word.strip().translate(None,string.punctuation))
	
	#initialize the knowledgebase for Flavor
	for i in range(0,len(knowledgeBaseFlavorFileName)):
		for j,line in enumerate(open('flavor/'+knowledgeBaseFlavorFileName[i],'r')):
			knowledgeBaseFlavor[i].add(line.strip().lower().translate(None,string.punctuation)) 

	#this is the total number of ingredients contains in the receipe
	TotalFoodNum = len(myFood["foodIngredient"])
	#analysis the ingredient in the receipe.
	
	meat      = 0
	vegetable = 1
	herb      = 2
	NA        = 3 #NA means not find the attribute map to this.

	ingredientClassify = {}
	for ingredient in myFood["foodIngredient"]:
		#use nltk to get the real food name.
		ingredientWord=set(ingredient.encode('utf-8').translate(None,string.punctuation).lower().split())
		index = NA		#the initial index is undefined
		maxmatch = 0
		for i in range(0,len(knowledgeBaseType)):
			if len(knowledgeBaseType[i]&ingredientWord)>maxmatch:
				index = i
				maxmatch = len(knowledgeBaseType[i]&ingredientWord)
		#get the most word that appears in the database.

		flavorIndex = NA+1 #this is the NA for the flavor part
		maxFlavorMatch = 0
		for i in range(0,len(knowledgeBaseFlavor)):
			if len(knowledgeBaseFlavor[i]&ingredientWord)>maxFlavorMatch:
				flavorIndex = i
				maxFlavorMatch = len(knowledgeBaseFlavor[i]&ingredientWord)
		ingredientClassify[ingredient]= str(index)+","+str(flavorIndex)
	#generate the detailed for the region
	for i,line in enumerate(open('region/'+region+'R','r')):
		if line.find('#')<0 and line!="":
			foodname = line.lower().split(',')[0]
			foodType = line.lower().split(',')[1]
			if foodType.find("vegetable")>=0:
				RegionvegetableSet.add(foodname)
			elif foodType.find("herb")>=0:
				RegionherbSet.add(foodname)
			else:
				RegionproteinSet.add(foodname)
		for j in range(0,len(knowledgeBaseFlavor)):
			if foodname in knowledgeBaseFlavor[j]:
				RegionFlavorSet[j].add(foodname)

	changeMap = {}
	substitue = ceil(TotalFoodNum*0.6) #to convert this menu, we need transform 50% of the ingredient
	emptyMap = {}
	for i in range(0,int(substitue)):
		lastKey = ""
		doChanged = False
		for key in ingredientClassify:
			content = ingredientClassify[key]
			if content =="":
				continue
			[foodtype,flavor] = ingredientClassify[key].split(",")
			if foodtype<NA and flavor<NA+1:     #this means the it contains both identified valid data
				ingredientClassify[key] = ""    #remove the data from consideration
				candidate = list(RegionFlavorSet[flavor]&RegionTypeSet[foodtype])
				newKey = candidate[randint(0,len(candidate)-1)]
				emptyMap[newKey] = ""
				changeMap[key] = newKey
				doChanged = True
				break
			elif flavor<NA+1:					#this means it contains the same flavor food
				ingredientClassify[key] = ""
				candidate = list(RegionFlavorSet[flavor])
				newKey = candidate[randint(0,len(candidate)-1)]
				emptyMap[newKey] = ""
				changeMap[key] = newKey
				doChanged = True
				break
			elif foodtype<NA:					#this means it contains the same type food.
				ingredientClassify[key] = ""
				candidate = list(RegionTypeSet[foodType])
				newKey = candidate[randint(0,len(candidate)-1)]
				emptyMap[newKey] = ""
				changeMap[key] = newKey
				doChanged = True
				break
			else:
				doChanged = False
				lastKey = key
		
		if doChanged==False:
			#this is do not contain the region type food.
			#print lastKey
			ingredientClassify[lastKey] = ""
			#default the candidate to be vegetable
			candidate = list(RegionTypeSet[vegetable])
			newKey = candidate[randint(0,len(candidate)-1)]
			emptyMap[newKey] = ""
			changeMap[lastKey] = newKey
	for key in ingredientClassify:
		if ingredientClassify[key]=="":
			continue
		else:
			emptyMap[key] = ""
	#start the mingle the ingredient
	orignDirection = myFood["directions"]
	newDirection   = []

	for d in orignDirection:
		for key in changeMap:
			d = d.replace(key,changeMap[key])
		newDirection.append(d)
	for key in changeMap:
		myindex = mapIndex[key]
		paredData[myindex]["ingredient"] = changeMap[key] 
	return newDirection,paredData


buildCountry = ["mexico","chinese","japanese"]

def buildSoup(url):
	print url
	try:
		user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
		hdr = {'User-Agent' : user_agent}
		req = urllib2.Request(url,headers=hdr)
		html = urllib2.urlopen(req)
	except urllib2.HTTPError,e:
		print "deadlink!"
	try:
		soup = BeautifulSoup(html)
	except:
		print "invalid data!"	
	return soup

def retrieveWeb(url):
	fooddict = {}
	foodResult = {}
	fooddirction = []
	soup = buildSoup(url)
	for pond in soup.find_all("li",{"id":"liIngredient"}):
		if pond.find("span",{"id":"lblIngAmount"}) != None:
			fooddict[pond.find("span",{"id":"lblIngName"}).text] = pond.find("span",{"id":"lblIngAmount"}).text
	foodResult["foodIngredient"] = fooddict
	dircection = soup.find("div", {"itemprop":"recipeInstructions"})
	foodDirection = []
	for li in dircection.find_all("li"):
		foodDirection.append(li.text)
	foodResult["directions"] = foodDirection
	return foodResult

def generateFoodOrigin(country,NoTcondition=[]):
	global buildCountry
	countryFood = {}
	url = "http://allrecipes.com/search/default.aspx?wt=#&Page=@"
	if len(NoTcondition)>0:
		for i in range(0,len(NoTcondition)):
			url+=("&u"+str(i)+"="+NoTcondition[i])
	countryFood[country] = {}
	for i in range(1,6):
		print "retrieve "+country+" Page:"+str(i)			
		realUrl = url.replace("#",country).replace("@",str(i)) #injection number here
		soup = buildSoup(realUrl)
		count = 0
		for grid in soup.find_all("div",{"id":"divGridItemWrapper"}):
			link = grid.find("a",{"class","img-link"})
			if link!=None:
				retrieve = retrieveWeb("http://allrecipes.com/"+link["href"])
				foodname = link.find("img")["title"]
				countryFood[country][foodname] = retrieve 
				count+=1
		print count
	return countryFood[country]

def buildFoodDataBase():
	global buildCountry
	foodKnowledgeBase = {}
	for country in buildCountry:
		food=generateFoodOrigin(country)
		foodKnowledgeBase[country] = {}
		for foodname in food: #the foodname is the receipe name
			foodKnowledgeBase[country][foodname] = []
			for ingredient in food[foodname]["foodIngredient"]:
				parseName = getIngredient(ingredient).encode('utf-8').translate(None,string.punctuation)
				foodKnowledgeBase[country][foodname].append(parseName)
	result = json.dumps(foodKnowledgeBase)
	with open('region.json', 'w') as out_file:
		out_file.write(result)	
	return foodKnowledgeBase

def main():
	print "Please run gui.py to execute program."

if __name__ == '__main__':
	main()