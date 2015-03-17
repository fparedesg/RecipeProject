from bs4 import BeautifulSoup
import urllib2
import nltk
from pprint import pprint
import re
import gui

# Our files

unitAbbreviations = {
	'c' : 'cup',
	'cs' : 'cup',
	'doz' : 'dozen',
	'fl' : 'fluid ounce',
	'fluid' : 'fluid ounce',
	'g' : 'gram',
	'gs' : 'gram',
	'gal' : 'gallon',
	'gals' : 'gallons',
	'in' : 'inch',
	'ins' : 'inches',
	'kg' : 'kilogram',
	'kgs' : 'kilograms',
	'l' : 'liter',
	'ls' : 'liters',
	'lb' : 'pound',
	'lbs' : 'pounds',
	'lg' : 'large',
	'med' : 'medium',
	'mg' : 'miligram',
	'mgs' : 'miligrams',
	'min' : 'minutes',
	'mins' : 'minutes',
	'ml' : 'mililiter',
	'mls' : 'mililiters',
	'oz' : 'ounce',
	'ozs' : 'ounces',
	'pkg' : 'package',
	'pkgs' : 'packages',
	'pt' : 'pint',
	'pts' : 'pints',
	'qt' : 'quart',
	'qts' : 'quarts',
	'sm' : 'small',
	'sq' : 'square',
	't' : 'teaspoon',
	'ts' : 'teaspoons',
	'tbsp' : 'tablespoon',
	'tbsps' : 'tablespoons',
	'tsp' : 'teaspoon',
	'tsps' : 'teaspoons',
	'#' : 'pound'
}

ingredientTitle = None

#this method is used to retrieve the information about the food name,quantity and the direction.
def retrieveWeb(url):
	foodDict = []
	foodResult = {}
	foodDirection = []
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

	for pond in soup.find_all("li", {"id":"liIngredient"} ):
		if pond.find("span", {"id":"lblIngAmount"} ) != None:
			foodDict.append([pond.find("span", {"id":"lblIngName"} ).text, pond.find("span", {"id":"lblIngAmount"} ).text])
	foodResult["foodname"] = foodDict
	dircection = soup.find("div", {"itemprop":"recipeInstructions"} )
	for li in dircection.find_all("li"):
		foodDirection.append(li.text)
	foodResult["directions"] = foodDirection

	global ingredientTitle
	ingredientTitle = soup.find("h1", {"id":"itemTitle"}).text
	
	return foodResult

# def getIngredient(unparsedIngredient):
# 	ingredient = ""
# 	# Extract nouns and pronouns
# 	for tag in nltk.pos_tag(nltk.word_tokenize(unparsedIngredient)):
# 		if("NN" in tag[1] or "PR" in tag[1]):
# 			ingredient += tag[0] + " "
# 	# If string ends in a space, remove it
# 	if ingredient != "" and ingredient[-1] == " ":
# 		ingredient = ingredient[:-1]
# 	# Return ingredient, or N/A if it is blank
# 	return ingredient if ingredient != "" else "N/A"

# def getDescriptorFromIngredient(ingredient):
# 	descriptor = ""
# 	# Extract adjectives, adverbs, and prepositional phrases
# 	for tag in nltk.pos_tag(nltk.word_tokenize(ingredient)):
# 		if("JJ" in tag[1] or "RB" in tag[1] or "IN" in tag[1]):
# 			descriptor += tag[0] + " "
# 	# If string ends in a space, remove it
# 	if descriptor != "" and descriptor[-1] == " ":
# 		descriptor = descriptor[:-1]
# 	# Return descriptor, or N/A if it is blank
# 	return descriptor if descriptor != "" else "N/A"

# def getPreparationFromIngredient(ingredient):
# 	preparation = ""
# 	# Extract verbs
# 	for tag in nltk.pos_tag(nltk.word_tokenize(ingredient)):
# 		if("VB" in tag[1]):
# 			preparation += tag[0] + " "
# 	# If string ends in space, remove it
# 	if preparation != "" and preparation[-1] == " ":
# 		preparation = preparation[:-1]
# 	# Return preparation, or N/A if it is blank
# 	return preparation if preparation != "" else "N/A"

def getAmountFromIngredient(ingredient):
	pattern = re.compile(r'(?:(?:\d+ )?(?:\d+/\d*)|(?:\d+\.\d*))?\d+') # W*N/M or N.M or N, where N,M,W are a numbers with any amount of digits
	unparsedNumber = pattern.findall(ingredient)[-1] # Find the last number in the string with the previous line's format
	parsedNumber = "NaN"
	if '/' in unparsedNumber:
		# Separate whole and fractional parts and parse to float
		pattern = re.compile(r'(?:(\d+) )?(\d+)/(\d+)')
		match = pattern.match(unparsedNumber)
		parsedNumber = (float(match.group(1)) if match.group(1) != None else 0) + float(match.group(2)) / float(match.group(3))
	else:
		# Otherwise just parse the number directly
		parsedNumber = float(unparsedNumber)
	return parsedNumber

def getUnitFromIngredient(ingredient):
	# Get the word directly after the amount
	ingredient = re.sub(r"(?:\(|\))", "", ingredient)
	pattern = re.compile(r'.*\d ([^ \d]+)') # Captures single word after digit followed by a space
	match = pattern.match(ingredient)
	unit = ""
	if match != None:
		# Get word after last number
		unparsedUnit = pattern.findall(ingredient)[-1]
		# Substitute unit abbreviation to unit, if needed
		unparsedUnit = unparsedUnit if unparsedUnit[-1].isalpha() else unparsedUnit[0:-1] # Remove last character is non alphabetic (e.g. for periods)
		if unparsedUnit.lower() in unitAbbreviations:
			unparsedUnit = unitAbbreviations[unparsedUnit]
		# Turn unit from plural to singular, if needed
		if unparsedUnit not in ["cloves", "ounces"]:
			unit = unparsedUnit[:-2] if unparsedUnit[-2:] == "es" else unparsedUnit[:-1] if unparsedUnit[-1] == "s" else unparsedUnit;
		else:
			unit = unparsedUnit
	return unit.lower()

def getPreparationFromIngredient(ingredient):
	# Remove all text within parenthesis
	ingredient = re.sub(r'\([^)]*\)', '', ingredient)
	# Remove all non-alphanumeric characters
	ingredient = re.sub(r'[^A-Za-z0-9- ]+', '', ingredient)
	# Find words that end in "ed", or that end in "t" and are classified as verbs by NLTK (like 'cut', 'went', 'bought', 'forgot', etc.)
	edWords = [word for word in ingredient.split() if word.endswith("ed")]
	tVerbs = [word[0] for word in nltk.pos_tag(nltk.word_tokenize(ingredient)) if word[0].endswith('t') and "VB" in word[1]]
	return ", ".join(list(set(edWords + tVerbs))).lower()

def getPreparationDescriptionFromIngredient(ingredient):
	# Remove all text within parenthesis
	ingredient = re.sub(r'\([^)]*\)', '', ingredient)
	# Remove all non-alphanumeric characters
	ingredient = re.sub(r'[^A-Za-z0-9- ]+', '', ingredient)
	# Find words that end in "ly", or that end in "y" and are classified by NLTK as adverbs (like 'very')
	lyWords = [word for word in ingredient.split() if word.endswith("ly")]
	yAdverbs = [word[0] for word in nltk.pos_tag(nltk.word_tokenize(ingredient)) if word[0].endswith('y') and "RB" in word[1]]
	return ", ".join(list(set(lyWords + yAdverbs))).lower()

def getIngredientAndDescriptorFromIngredient(ingredient, preparation, preparationDescription):
	# Remove all text within parenthesis
	ingredient = re.sub(r'\([^)]*\)', '', ingredient)
	# Remove all non-alphanumeric characters
	ingredient = re.sub(r'[^A-Za-z0-9- ]+', '', ingredient)
	# Remove all words used in preparation and preparation description
	for p in preparation.split(", "):
		ingredient = ingredient.replace(p, "")
	for p in preparationDescription.split(", "):
		ingredient = ingredient.replace(p, "")
	# All adjectives will be descriptors, and everything else will be the ingredient
	descriptors = [word[0] for word in nltk.pos_tag(nltk.word_tokenize(ingredient)) if "JJ" in word[1]]
	for descriptor in descriptors:
		ingredient = ingredient.replace(descriptor, "")
	ingredient = ingredient.strip()
	# Change the descriptor to be the ingredient iff the ingredient is currently the empty string
	if not ingredient:
		ingredient = ", ".join(descriptors)
		descriptors = []
	# Finally, return
	return re.sub(r' +', ' ', ingredient).lower(), ", ".join(descriptors).lower()

def CorrectDescriptor(ingredient):
# If the ingredient contains the word "into", it will stuff everything after "into" into the
#  preparation description and remove it from the ingredient
	if "into" in ingredient["ingredient"]:
		# Get everything that comes after "into"
		pattern = re.compile(r".+(into.+)$")
		everythingThatComesAfterInto = pattern.match(ingredient["ingredient"]).group(1)
		# And either set it as preparationDescription if empty, or append it at the end otherwise
		if ingredient["preparationDescription"]:
			preparationDescriptionArray = ingredient["preparationDescription"].split(", ")
			preparationDescriptionArray.append(everythingThatComesAfterInto)
			ingredient["preparationDescription"] = ", ".join(preparationDescriptionArray)
		else:
			ingredient["preparationDescription"] = everythingThatComesAfterInto
		ingredient["ingredient"] = ingredient["ingredient"].replace(everythingThatComesAfterInto, "")
	# On the off chance that the ingredient is STILL empty, then something went SERIOUSLY wrong with the parser, so just append everything into the ingredient
	if not ingredient["ingredient"]:
		ingredient["ingredient"] = ingredient["descriptor"] + ingredient["preparation"] + ingredient["preparationDescription"]
		ingredient["descriptor"] = ingredient["preparation"] = ingredient["preparationDescription"] = ""


def createDictionaries(webData):
	directions = webData["directions"]
	for d, direction in enumerate(directions):
		directions[d] = direction.lower()
	ingredients = []

	for e in webData["foodname"]:
		ingredient = {}
		ingredient["amount"] = getAmountFromIngredient(e[1])
		ingredient["unit"] = getUnitFromIngredient(e[1])
		ingredient["preparation"] = getPreparationFromIngredient(e[0])
		ingredient["preparationDescription"] = getPreparationDescriptionFromIngredient(e[0])
		ingredient["ingredient"], ingredient["descriptor"] = getIngredientAndDescriptorFromIngredient(e[0], ingredient["preparation"], ingredient["preparationDescription"])
		CorrectDescriptor(ingredient)
		ingredients.append(ingredient)

	return directions, ingredients

def readFromFile(filename):
	with open(filename, 'r') as in_file:
		jsondict = eval(in_file.read())	
		return jsondict	

def getIngredientsForStep(step, ingredients):
	stepWords = step.split()

	for i, word in enumerate(stepWords):
		if not word[-1].isalnum():
			stepWords[i] = stepWords[i][:-1]
			
	stepIngredients = []

	for ingredient in ingredients:
		if any (word in stepWords for word in ingredient['ingredient'].split()):
			if ingredient['ingredient'] not in stepIngredients:
				stepIngredients.append(ingredient['ingredient'])

	return stepIngredients

def getMethodsForStep(step):

	stepMethods = []

	for method in readFromFile("knowledgebase.txt")["methods"]:
			if method in step and method + "ed" not in step:
				stepMethods.append(method)

	return stepMethods

def getToolsForStep(step):

	stepTools = []

	for tool in readFromFile("knowledgebase.txt")["tools"]:
			if tool in step:
				stepTools.append(tool)

	return stepTools


def getTimesForStep(step):
	pattern = re.compile(r'[^0-9]+(?:(\d+) to )?(\d+) (hours*|minutes*)')

	stepTimes = []

	for sentence in step.split('. '):
		for phrase in sentence.split('degrees '):
			if not phrase[-1].isalnum():
				phrase = phrase[:-1]
			match = pattern.match(phrase)		
	
		if match is not None:

			if match.group(1) is not None:
				stepTimes.append(match.group(1) + " to " + match.group(2) + " " + match.group(3))

			else:
				stepTimes.append(match.group(2) + " " + match.group(3))

		else:

			pattern = re.compile(r'[^0-9]+(?:(\d+ )?(?:(\d+)/(\d*))) (hours*|minutes*)') # W*N/M or N.M or N, where N,M,W are a numbers with any amount of digits
			match = pattern.match(phrase)

			if match is not None:
				num0 = float(match.group(1))
				num1 = float(match.group(2))
				num2 = float(match.group(3))
				unit = match.group(4)

				stepTimes.append(str(num0 + num1/num2) + " " + unit)

					

	return stepTimes

def getPrimaryMethod(methods):
# The knowledge base has the possible methods as an ordered list.
#  The higher it is on the list, the more likely it is to be a primary method.
#  This method simply finds the first one that is listed in each of the steps' methods and returns that.
	for method in readFromFile("knowledgebase.txt")["methods"]:
		if method in methods:
			return method
	return None

def consolidateData(parsedDirections):
# Consolidates information from all steps and removes repeated elements
	methods = []
	tools = []
	for step in parsedDirections:
		methods += step["methods"]
		tools += step["tools"]
	return list(set(methods)), list(set(tools))

def parseDirections(directions, ingredients):
	parsedDirections = []
	for i, step in enumerate(directions):
		parsedDirections.append({})
		parsedDirections[i]['text'] = step
		parsedDirections[i]['ingredients'] = getIngredientsForStep(step, ingredients)
		parsedDirections[i]['methods'] = getMethodsForStep(step)
		parsedDirections[i]['tools'] = getToolsForStep(step)
		parsedDirections[i]['times'] = getTimesForStep(step)	

	return parsedDirections	

def main():
	print "Please run gui.py to execute program."

if __name__ == '__main__':
	main()