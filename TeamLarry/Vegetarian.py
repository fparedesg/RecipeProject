import ParseRecipe
import gui

from random import choice
import re

def readFromFile(filename):
	with open(filename, 'r') as in_file:
		jsondict = eval(in_file.read())	
		return jsondict

def CheckIfIsBread(directions, ingredients, ingredientNumber):
	isBread = False
	breadStuff = ["bread", "pancake", "hotcake", "muffin", "cake", "cookie", "brownie", "loaf"]
	# Only check title for keywords in previous line
	if [ing for ing in breadStuff if ing in ParseRecipe.ingredientTitle.lower()]:
		isBread = True
	# Make appropriate substitution with egg used as a leavening agent
	if isBread:
		ingredients[ingredientNumber]["preparation"] = "ground"
		ingredients[ingredientNumber]["unit"] = "tablespoon"
		ingredients[ingredientNumber]["ingredient"] = "flax seed"
		for j, step in enumerate(directions):
			directions[j] = directions[j].replace(" egg", " flax seed")
	return isBread

def MakeDefaultEggSubstitutions(directions, ingredients, ingredientNumber):
	ingredients[ingredientNumber]["amount"] = 0.75*ingredients[ingredientNumber]["amount"]
	ingredients[ingredientNumber]["unit"] = "cup"
	ingredients[ingredientNumber]["ingredient"] = u"silken tofu"
	for j, step in enumerate(directions):
		directions[j] = directions[j].replace(" egg", " silken tofu")

def MakeVegetarian(directions, ingredients):
	print "\n\nLet's make a vegeterian meal!\n"
	isVegetarian = True
	knowledgebase = readFromFile("knowledgebase.txt")["ingredients"]
	meats = {meat: knowledgebase[meat] for meat in knowledgebase if "meat" in knowledgebase[meat]['roles']}
	fish = {fish: knowledgebase[fish] for fish in knowledgebase if "fish" in knowledgebase[fish]['roles']}
	# For each ingredient in recipe
	for i, recipeIngredientInfo in enumerate(ingredients):
		recipeIngredient = recipeIngredientInfo["ingredient"]
		# Check if ingredient is listed as a meat
		hasMeat = [[e, meats[e]["sub"]] for e in meats if "sub" in meats[e] and (recipeIngredient in e or e in recipeIngredient)]
		hasFish = [[e, fish[e]["sub"]] for e in fish if "sub" in fish[e] and (recipeIngredient in e or e in recipeIngredient)]
		if hasMeat or hasFish:
			isVegetarian = False
			# If it is either meaty or fishy, first substitute ingredient name with match
			if hasMeat:
				# Special case if the 'meat' is an egg
				if hasMeat[0][0] == "egg":
					if not CheckIfIsBread(directions, ingredients, i):
						MakeDefaultEggSubstitutions(directions, ingredients, i)
					continue
		 		ingredients[i]["ingredient"] = ingredients[i]["ingredient"].replace(hasMeat[0][0], hasMeat[0][1])
		 		# And do the same for the string matches in the directions list
		 		for j, step in enumerate(directions):
					directions[j] = directions[j].replace(" " + hasMeat[0][0], " " + hasMeat[0][1])
		 	elif hasFish:
		 		ingredients[i]["ingredient"] = ingredients[i]["ingredient"].replace(hasFish[0][0], hasFish[0][1])
		 		for j, step in enumerate(directions):
					directions[j] = directions[j].replace(" " + hasFish[0][0], " " + hasFish[0][1])
					directions[j] = directions[j].replace(" fish", " " + hasFish[0][1])
	# Finally, return
	if isVegetarian:
		print "This recipe was already vegetarian! No changes were made to the recipe."
	return directions, ingredients

def MakeUnVegetarian(directions, ingredients):
	print "\n\nLet's make a meal with meat of some sort!\n"
	isVegetarian = False
	knowledgebase = readFromFile("knowledgebase.txt")["ingredients"]
	vegetarianProteins = {veg: knowledgebase[veg] for veg in knowledgebase if "vegetarianProtein" in knowledgebase[veg]['roles']}
	# For each ingredient in recipe
	for i, recipeIngredientInfo in enumerate(ingredients):
		recipeIngredient = recipeIngredientInfo["ingredient"]
		# Check if ingredient is listed as a vegetarian protein
		hasVegetarianProtein = [[e, vegetarianProteins[e]["sub"]] for e in vegetarianProteins if "sub" in vegetarianProteins[e] and recipeIngredient in e] + [[e, vegetarianProteins[e]["sub"]] for e in vegetarianProteins if "sub" in vegetarianProteins[e] and recipeIngredient]
		if hasVegetarianProtein:
			isVegetarian = True
			# Substitute ingredient in list
			ingredients[i]["ingredient"] = ingredients[i]["ingredient"].replace(hasVegetarianProtein[0][0], hasVegetarianProtein[0][1])
			# And in directions
			for j, step in enumerate(directions):
				directions[j] = directions[j].replace(" " + hasVegetarianProtein[0][0], " " + hasVegetarianProtein[0][1])
	# Finally, return
	if not isVegetarian:
		print "This recipe appears to contain no vegetarian proteins! No changes were made to the recipe."
	return directions, ingredients

def MakePescatarian(directions, ingredients):
	print "\n\nLet's make a pescatarian meal!\n"
	isPescatarian = True
	knowledgebase = readFromFile("knowledgebase.txt")['ingredients']
	meats = {meat: knowledgebase[meat] for meat in knowledgebase if "meat" in knowledgebase[meat]['roles']}
	# For each ingredient in recipe
	for i, recipeIngredientInfo in enumerate(ingredients):
		recipeIngredient = recipeIngredientInfo["ingredient"]
		# Check if ingredient is listed as a meat
		hasMeat = [[e, meats[e]["sub"]] for e in meats if "sub" in meats[e] and (recipeIngredient in e or e in recipeIngredient)]
		if hasMeat:
			isPescatarian = False
			# Special case if the 'meat' is an egg
			if hasMeat[0][0] == "egg":
				if not CheckIfIsBread(directions, ingredients, i):
					MakeDefaultEggSubstitutions(directions, ingredients, i)
				continue
		 	ingredients[i]["ingredient"] = ingredients[i]["ingredient"].replace(hasMeat[0][0], hasMeat[0][1])
		 	# And do the same for the string matches in the directions list
		 	for j, step in enumerate(directions):
				directions[j] = directions[j].replace(" " + hasMeat[0][0], " " + hasMeat[0][1])
	# Finally, return
	if isPescatarian:
		print "This recipe was already pescatarian! No changes were made to the recipe."
	return directions, ingredients

def MakeUnPescatarian(directions, ingredients):
# This one will be a bit different than MakeUnVegetarian. MakeUnVegetarian only substitutes vegetarian
#  proteins for various meats, depending on which vegetarian protein is being changed. MakeUnPescatarian
#  will also consider the fish products and for chicken, because chicken's awesome.
	print "\n\nLet's make a meal with meat of some sort!\n"
	isPescatarian = False
	knowledgebase = readFromFile("knowledgebase.txt")['ingredients']
	vegetarianProteins = {veg: knowledgebase[veg] for veg in knowledgebase if "vegetarianProtein" in knowledgebase[veg]['roles']}
	fish = {fish: knowledgebase[fish] for fish in knowledgebase if "fish" in knowledgebase[fish]['roles']}
	# For each ingredient in recipe
	for i, recipeIngredientInfo in enumerate(ingredients):
		recipeIngredient = recipeIngredientInfo["ingredient"]
		# Check if ingredient is listed as a vegetarian protein or fish
		hasVegetarianProtein = [[e, vegetarianProteins[e]["sub"]] for e in vegetarianProteins if "sub" in vegetarianProteins[e] and recipeIngredient in e] + [[e, vegetarianProteins[e]["sub"]] for e in vegetarianProteins if "sub" in vegetarianProteins[e] and e in recipeIngredient]
		hasFish = [[e, fish[e]["sub"]] for e in fish if "sub" in fish[e] and (recipeIngredient in e or e in recipeIngredient)]
		if hasVegetarianProtein:
			isPescatarian = True
			# Substitute ingredient in list
			# If substitute word is "tofurky", also replace entire ingredient with ham; otherwise replace accordingly
			ingredients[i]["ingredient"] = "ham" if hasVegetarianProtein[0][0] == "tofurky" else ingredients[i]["ingredient"].replace(hasVegetarianProtein[0][0], hasVegetarianProtein[0][1])
			# And in directions
			for j, step in enumerate(directions):
				# If substitute word is "tofurky", also replace word after it (e.g. for tofurky sausage, tofurky ham, etc.)
				if hasVegetarianProtein[0][0] == "tofurky":
					directions[j] = re.sub(r"tofurky [A-Za-z]+", hasVegetarianProtein[0][1], directions[j])
				# else just substitute ingredient normally
				else:
					directions[j] = directions[j].replace(" " + hasVegetarianProtein[0][0], " " + hasVegetarianProtein[0][1])
		elif hasFish:
			isPescatarian = True
			ingredients[i]["ingredient"] = "chicken breast"
			if hasFish[0][1] != "tempeh": # if fish is, well, not a fish (i.e. a mollusk, shrimp, crab, etc.)
				# Make it so that the chicken breast preparation style is cubed
				ingredients[i]["preparation"] = "cubed"
			# And substitute directions as well
			for j, step in enumerate(directions):
				directions[j] = directions[j].replace(" " + hasFish[0][0], " chicken breast")
	if not isPescatarian:
		print "This meal already contains no vegetarian proteins or fish! No changes were made to the recipe."
	return directions, ingredients

def main():
	print "Please run gui.py to execute program."

if __name__ == '__main__':
	main()