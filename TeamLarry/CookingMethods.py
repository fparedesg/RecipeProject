import ParseRecipe
import gui
from pprint import pprint


def readFromFile(filename):
	with open(filename, 'r') as in_file:
		jsondict = eval(in_file.read())	
		return jsondict



def MakeAStirFry(ingredients):
	print "\n\nLet's make a stir fry meal!"

	stirFryDirections = ["Bring rice and water to a boil in a saucepan over high heat. Reduce heat to medium-low, cover, and simmer until rice is tender, and liquid has been absorbed, 20 to 25 minutes."]

	knowledgebase = readFromFile("knowledgebase.txt")["ingredients"]

	meats = {meat: knowledgebase[meat] for meat in knowledgebase if "meat" in knowledgebase[meat]['roles']}
	vegetables =  {vegetable: knowledgebase[vegetable] for vegetable in knowledgebase if "fruit/vegetable" in knowledgebase[vegetable]['roles']}

	stirFryMeats = []
	stirFryVegetables =[]

	for i, recipeIngredientInfo in enumerate(ingredients):
		recipeIngredient = recipeIngredientInfo["ingredient"]
		if [e for e in meats if recipeIngredient in e or e in recipeIngredient] != [] and recipeIngredient != "mayonnaise":
			stirFryMeats.append(recipeIngredient)
		if [e for e in vegetables if recipeIngredient in e or e in recipeIngredient] != []:
			stirFryVegetables.append(recipeIngredient)

	if stirFryMeats != []:
		stirFryDirections.append("Slice " + ', '.join(stirFryMeats) + " into very thin strips.")
		stirFryDirections.append("Heat 1 tablespoon oil in saucepot or wok over high heat. Add " + ', '.join(stirFryMeats) + " and stir fry until browned. Set " + ', '.join(stirFryMeats) + " aside.")
	
	if stirFryVegetables != []:
		stirFryDirections.append("Add 1 tablespoon oil. Add the " + ', '.join(stirFryVegetables) + " and stir fry over medium heat until tender-crisp. Set vegetables aside.")

	stirFryDirections.append("Return protein and vegetables to saucepot and heat through. Serve over rice.")

	stirFryIngredients = []

	for stirFryIngredient in ingredients:
		if stirFryIngredient['ingredient'] in stirFryMeats:
			ingredient = {}
			ingredient["amount"] = stirFryIngredient["amount"]
			ingredient["unit"] = stirFryIngredient["unit"]
			ingredient["preparation"] = "sliced"
			ingredient["preparationDescription"] = "thinly"
			ingredient["ingredient"] = stirFryIngredient["ingredient"]
			ingredient["descriptor"] = stirFryIngredient["descriptor"]
			ParseRecipe.CorrectDescriptor(ingredient)
			stirFryIngredients.append(ingredient)
		elif stirFryIngredient['ingredient'] in stirFryVegetables:
			ingredient = {}
			ingredient["amount"] = stirFryIngredient["amount"]
			ingredient["unit"] = stirFryIngredient["unit"]
			ingredient["preparation"] = "sliced"
			ingredient["preparationDescription"] = ""
			ingredient["ingredient"] = stirFryIngredient["ingredient"]
			ingredient["descriptor"] = stirFryIngredient["descriptor"]
			ParseRecipe.CorrectDescriptor(ingredient)
			stirFryIngredients.append(ingredient)

	if not any("rice" == myingredient["ingredient"] for myingredient in stirFryIngredients):
		ingredient = {}
		ingredient["amount"] = 2.0
		ingredient["unit"] = "cup"
		ingredient["preparation"] = ""
		ingredient["preparationDescription"] = ""
		ingredient["ingredient"] = "rice"
		ingredient["descriptor"] = "white"
		stirFryIngredients.append(ingredient)

	if not any("oil" in myingredient["ingredient"] for myingredient in stirFryIngredients):
		ingredient = {}
		ingredient["amount"] = 2.0
		ingredient["unit"] = "tablespoon"
		ingredient["preparation"] = ""
		ingredient["preparationDescription"] = ""
		ingredient["ingredient"] = "sesame oil"
		ingredient["descriptor"] = ""
		stirFryIngredients.append(ingredient)	
			
	return stirFryDirections,stirFryIngredients


def main():
	print "Please run gui.py to execute program."

if __name__ == '__main__':
	main()