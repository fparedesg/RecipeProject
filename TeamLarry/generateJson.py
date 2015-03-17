import json
import ParseRecipe
from math import ceil
import sys
import pprint

def generateResultJson(url):
	jsonResult = {}
	#seal the url field
	jsonResult["url"] = url
	rawdata = ParseRecipe.retrieveWeb(url)
	jsonResult["ingredients"] = []
	directions, ingredients =ParseRecipe.createDictionaries(rawdata)
	totalCount = 0
	for ingredient in ingredients:
		parsedIngredient = {}
		parsedIngredient["name"] = ingredient["ingredient"]
		parsedIngredient["quantity"] = ingredient["amount"]
		parsedIngredient["measurement"] = ingredient["unit"]
		parsedIngredient["descriptor"] = ingredient["descriptor"]
		parsedIngredient["preparation"] = ingredient["preparation"]
		parsedIngredient["prep-description"] = ingredient["preparationDescription"]
		jsonResult["ingredients"].append(parsedIngredient)
	parsedDirections = ParseRecipe.parseDirections(directions, ingredients)
	methods, tools = ParseRecipe.consolidateData(parsedDirections)
	primaryMethod = ParseRecipe.getPrimaryMethod(methods)
	jsonResult["primary cooking method"] = primaryMethod
	jsonResult["cooking methods"] = methods
	jsonResult["cooking tools"] = tools
	#this part generate the tools
	# toolSet = set()
	# cookingMethod = {}
	# totalCookingMethod = 0
	# for item in parsedDirections:
	# 	for tool in item["tools"]:
	# 		toolSet.add(tool)
	# 	for cook in item["methods"]:
	# 		totalCookingMethod +=1
	# 		if cook in cookingMethod:
	# 			cookingMethod[cook] += 1
	# 		else:
	# 			cookingMethod[cook] = 1
	# limit = ceil(totalCookingMethod*0.25)
	# jsonResult["primary cooking method"] = list()
	# for k,v in sorted(cookingMethod.iteritems(), key=lambda d:d[1], reverse = True):
	# 	if v>=limit:
	# 		jsonResult["primary cooking method"].append(k)
	# 	else:
	# 		break
	# jsonResult["cooking tools"] = list(toolSet)
	# jsonResult["cooking methods"] = []
	# for key in cookingMethod:
	# 	jsonResult["cooking methods"].append(key)
	
	result = json.dumps(jsonResult)
	
	return jsonResult

def generateJson(url):
	jsonResult = {}
	#seal the url field
	jsonResult["url"] = url
	rawdata = ParseRecipe.retrieveWeb(url)
	jsonResult["ingredients"] = []
	directions, ingredients =ParseRecipe.createDictionaries(rawdata)
	totalCount = 0
	for ingredient in ingredients:
		parsedIngredient = {}
		parsedIngredient["name"] = [ingredient["ingredient"]]
		parsedIngredient["quantity"] = [ingredient["amount"]]
		parsedIngredient["measurement"] = [ingredient["unit"]]
		parsedIngredient["descriptor"] = [ingredient["descriptor"]]
		parsedIngredient["preparation"] = [ingredient["preparation"]]
		parsedIngredient["prep-description"] = [ingredient["preparationDescription"]]
		count = 0
		for key in parsedIngredient:
			if  parsedIngredient[key][0]!='':
				count+=1
		parsedIngredient["max"]  = count #what is this field?
		totalCount +=count
		jsonResult["ingredients"].append(parsedIngredient)
	parsedDirections =ParseRecipe.parseDirections(directions, ingredients)
	#this part generate the tools
	toolSet = set()
	cookingMethod = {}
	totalCookingMethod = 0
	for item in parsedDirections:
		for tool in item["tools"]:
			toolSet.add(tool)
		for cook in item["methods"]:
			totalCookingMethod +=1
			if cook in cookingMethod:
				cookingMethod[cook] += 1
			else:
				cookingMethod[cook] = 1
	limit = ceil(totalCookingMethod*0.25)
	jsonResult["primary cooking method"] = list()
	for k,v in sorted(cookingMethod.iteritems(), key=lambda d:d[1], reverse = True):
		if v>=limit:
			jsonResult["primary cooking method"].append(k)
		else:
			break
	jsonResult["cooking tools"] = list(toolSet)
	jsonResult["cooking methods"] = []
	for key in cookingMethod:
		jsonResult["cooking methods"].append(key)
	jsonResult["max"] = {}
	jsonResult["max"]["ingredients"] = totalCount
	jsonResult["max"]["cooking methods"] = len(cookingMethod)
	jsonResult["max"]["cooking tools"]   = len(toolSet)
	jsonResult["max"]["primary cooking method"] = len(jsonResult["primary cooking method"])
	result = json.dumps(jsonResult)
	with open('recipe1.json', 'w') as out_file:
		out_file.write(result)
	return

def main():
	if len(sys.argv) != 2:
		print "Usage: python generateJson.py <url>"
		print "Exiting."
		sys.exit(0)

	else:
		url = sys.argv[1]

	pprint.pprint(generateResultJson(url))
	return generateResultJson(url)

if __name__ == '__main__':
	main()