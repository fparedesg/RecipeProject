from bs4 import BeautifulSoup
import urllib2
import json
import pymongo
import string
import re

READ_ME = "This script doesn't do anything anymore. This was used to build our initial knowledge base."

#this method is used to retrieve the information about the food name,quantity and the direction.
buildCountry = ["mexico","chinese","japanese"]
buildFalvor  = ["sweet","sour","spicy","bitter"]

def buildSoup(url):
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
	foodResult["foodname"] = fooddict
	dircection = soup.find("div",{"itemprop":"recipeInstructions"})
	for li in dircection.find_all("li"):
		fooddirction.append(li.text)
	foodResult["dircection"] = fooddirction
	return foodResult

def importFoodToMongoDB():
	conn = pymongo.Connection()
	db = conn.recipe
	foodlist = db.foodlist
	for i, line in enumerate(open("meat", 'r')):
		record = dict(name=line.lower().strip(),type="M",region=[]) #stands for the meat
		db.foodlist.insert(record)
	for i, line in enumerate(open("vegetable_all",'r')):
		record = dict(name=line.lower().strip(),type="V",region=[])
		db.foodlist.insert(record)
	return 

def generateFoodFlavor(flavor,NoTcondition=[]):
	global buildFalvor
	#http://allrecipes.com/search/default.aspx?wt=Mexico&Page=2
	#This is the url related to search
	FoodFlavor = {}
	url = "http://allrecipes.com/search/default.aspx?wt=#&Page=@"
	if len(NoTcondition)>0:
		for i in range(0,len(NoTcondition)):
			url+=("&u"+str(i)+"="+NoTcondition[i])
	FoodFlavor[flavor] = {}
	for i in range(1,6):
		print "retrieve "+flavor+" Page:"+str(i)			
		realUrl = url.replace("#",flavor).replace("@",str(i)) #injection number here
		soup = buildSoup(realUrl)
		count = 0
		for grid in soup.find_all("div",{"id":"divGridItemWrapper"}):
			link = grid.find("a",{"class","img-link"})
			if link!=None:
				retrieve = retrieveWeb("http://allrecipes.com/"+link["href"])
				retrieve["dircection"] = ""
				foodname = link.find("img")["title"]
				FoodFlavor[flavor][foodname] = retrieve 
				count+=1
		print count
	return FoodFlavor[flavor]

def generateFoodOrigin(country,NoTcondition=[]):
	global buildCountry
	#http://allrecipes.com/search/default.aspx?wt=Mexico&Page=2
	#This is the url related to search
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
				retrieve["dircection"] = ""
				foodname = link.find("img")["title"]
				countryFood[country][foodname] = retrieve 
				count+=1
		print count
	return countryFood[country]
#URLLIST = ["http://en.wikipedia.org/wiki/List_of_vegetables","http://en.wikipedia.org/wiki/List_of_culinary_herbs_and_spices","http://en.wikipedia.org/wiki/List_of_domesticated_meat_animals"]

#this actually shall work for all normalize method ..sorry for narrow mind
def retrieveRelated(radwdata,resultFile):
	#this can not be the word in the receipe, this actually can be analysised out..
	global buildCountry
	global buildFalvor
	verbList = [r'roast',r'polish',r'half',r'halv',r'trim(m)*',r'condense',r'rins',r'reserve',r'toast',r'color',r'crack',r'flake',r'can(n)*',r'pack',r'drain',r'fry',r'sift',r'[0-9]',r'peel',r'grate',r'heat',r'shred(d)*',r'mince',r'shred(d)*',r'deveine',r'dice',r'remove',r'divide',r'chop(p)*',r'(un)*cook',r'extract',r'ground',r'cut(t)*',r'crush',r'slice',r'bak(e|ing)',r'mix',r'wash',r'soft(en)*']
	reglist  = []
	stopSet  = set()
	for word in verbList:
		reglist.append(re.compile(word+"(ed|s|es|ing)*"))
	stopwordList = ['and','or','with','such','as','if','into','finely','to','of','for','from','back','inch','fresh']
	for word in stopwordList:
		stopSet.add(word)
	for word in buildCountry:
		stopSet.add(word)
	for word in buildFalvor:
		stopSet.add(word)
	foodRelatedTable = radwdata

	#this is the possible ingredient name for food..
	foodnameTable = {}
	conn = pymongo.Connection()
	db = conn.recipe
	for foodname in foodRelatedTable:
		foodIngredient = foodRelatedTable[foodname]["foodname"]
		for ingredient in foodIngredient:
			ingredient = ingredient.encode('utf-8')
			#delete the punctuation here
			delset = string.punctuation
			ingredient = ingredient.translate(None,delset).lower().split()
			ingredientWord = [] 
			#this is for the possible ingredient word
			for i,word in enumerate(ingredient):
				if any(regex.match(word) for regex in reglist) or word in stopSet or len(word)<3:
					continue
				buffer = []
				for ingredientName in ingredientWord:
					if ingredientName[len(ingredientName)-1] == ingredient[i-1]:
						temp = []
						for T in ingredientName:
							temp.append(T)
						buffer.append(temp)
						buffer[len(buffer)-1].append(word)
				for temp in buffer:
					ingredientWord.append(temp)
				ingredientWord.append([word])
			for c in ingredientWord:
				name  = ' '.join(c)
				if name in foodnameTable:
					foodnameTable[name]+=1
				else:
					foodnameTable[name] =1
	for k in foodnameTable:
		foodnameTable[k]*=len(k.split())
	finalResult = []
	for k,v in sorted(foodnameTable.iteritems(), key=lambda d:d[1], reverse = True):
		print k,v
		finalResult.append(k)
	with open(resultFile, 'w') as out_file:
		out_file.write('\n'.join(finalResult))
	return 

def retrieveRawData(srcfile,type):
	data = {}
	with open(srcfile, 'r') as f:
		data = json.load(f)
	return data[type]

def intersectData(file1,file2list):
	src = set()
	for i,line in enumerate(open(file1)):
		src.add(line.strip())
	dst = set()
	for dstfile in file2list:
		for i,line in enumerate(open(dstfile)):
			dst.add(line.strip())
	src = src-dst
	print src

def retrieveCountryData():
	global buildCountry
	countryDict = {}
	for country in buildCountry:
		countryDict[country] = generateFoodOrigin(country)
	result = json.dumps(countryDict)
	with open('result.json', 'w') as out_file:
		out_file.write(result)

def retriveFlavorData():
	global buildFalvor
	flavordict = {}
	for flavor in buildFalvor:
		flavordict[flavor] = generateFoodFlavor(flavor)
	result = json.dumps(flavordict)
	with open('Flavor.json', 'w') as out_file:
		out_file.write(result)	

def main():
	print "Please run gui.py to execute program."
	print READ_ME

if __name__ == '__main__':
	main()