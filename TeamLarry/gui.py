from Tkinter import *
import ParseRecipe
import Vegetarian
import CookingMethods
import Regionalize
import generateJson
from pprint import pprint


def main():

	master = Tk()

	l = Label(master, text="Recipe Project")
	l.grid(row=0, column=0, columnspan=5)

	e = Entry(master, width=55)
	e.grid(row=1, column=0, columnspan=2)
	e.delete(0, END)
	#e.insert(0, "http://allrecipes.com/Recipe/Good-Old-Fashioned-Pancakes/")
	e.insert(0, "http://allrecipes.com/Recipe/Oven-Baked-Jambalaya/") # This recipe is good for showing off the vegetarian/pescatarian thing!

	b = Button(master, text="Parse Recipe", command=lambda:generateOutputFile(e.get()), default=ACTIVE)
	b.grid(row=1, column=2)

	b = Button(master, text="Create Chinese Dish", command=lambda:changeMealByRegion(e.get(),"Chinese"))
	b.grid(row=2, column=0)

	b = Button(master, text="Create Japanese Dish", command=lambda:changeMealByRegion(e.get(),"Japanese"))
	b.grid(row=2, column=1)

	b = Button(master, text="Create Mexican Dish", command=lambda:changeMealByRegion(e.get(),"Mexican"))
	b.grid(row=2, column=2)

	b = Button(master, text="Create Stir Fry", command=lambda:changeMealByCookingMethod(e.get(),"Stir Fry"))
	b.grid(row=3, column=0)

	b = Button(master, text="Create Vegetarian Dish", command=lambda:changeMealToFromVegetarian(e.get(),"to"))
	b.grid(row=5, column=0)

	b = Button(master, text="Create Non-Vegetarian Dish", command=lambda:changeMealToFromVegetarian(e.get(),"from"))
	b.grid(row=5, column=1)

	b = Button(master, text="Create Pescatarian Dish", command=lambda:changeMealToFromPescatarian(e.get(),"to"))
	b.grid(row=6, column=0)

	b = Button(master, text="Create Non-Pescatarian Dish", command=lambda:changeMealToFromPescatarian(e.get(),"from"))
	b.grid(row=6, column=1)

	master.mainloop()

def changeMealByRegion(url, region):
	webData = ParseRecipe.retrieveWeb(url)
	directions,parsedData = ParseRecipe.createDictionaries(webData)
	print "Original Recipe: "
	prettyPrint(directions, parsedData)
	newDirections, newIngredients = Regionalize.MakeThisRegion(region.lower(),parsedData,directions) # Does not work with new updates
	prettyPrint(newDirections, newIngredients)

def changeMealByCookingMethod(url, method):
	webData = ParseRecipe.retrieveWeb(url)
	directions, ingredients = ParseRecipe.createDictionaries(webData)
	print "Original Recipe: "
	prettyPrint(directions, ingredients)
	newDirections, newIngredients = CookingMethods.MakeAStirFry(ingredients)
	prettyPrint(newDirections, newIngredients)

def changeMealToFromVegetarian(url, tofrom):
	webData = ParseRecipe.retrieveWeb(url)
	directions, ingredients = ParseRecipe.createDictionaries(webData)
	print "Original Recipe: "
	prettyPrint(directions, ingredients)
	if tofrom == "to":
		directions, ingredients = Vegetarian.MakeVegetarian(directions, ingredients)
	else:
		directions, ingredients = Vegetarian.MakeUnVegetarian(directions, ingredients)
	prettyPrint(directions, ingredients)

def changeMealToFromPescatarian(url, tofrom):
	webData = ParseRecipe.retrieveWeb(url)
	directions, ingredients = ParseRecipe.createDictionaries(webData)
	if tofrom == "to":
		directions, ingredients = Vegetarian.MakePescatarian(directions, ingredients)
	else:
		directions, ingredients = Vegetarian.MakeUnPescatarian(directions, ingredients)
	prettyPrint(directions, ingredients)

def generateOutputFile(url):	
	#generateJson.generateJson(url)
	pprint(generateJson.generateResultJson(url))
	print "Done generating output json file"

def Validate(string):
	# Simply returns string, or "N/A" if string is empty
	return string if string else "N/A"

def prettyPrint(directions, ingredients):
	parsedDirections = ParseRecipe.parseDirections(directions, ingredients)
	methods, tools = ParseRecipe.consolidateData(parsedDirections)
	primaryMethod = ParseRecipe.getPrimaryMethod(methods)

	print "\nINGREDIENTS"
	for i, ingredient in enumerate(ingredients):
		print "\tIngredient: " + ingredient["ingredient"]
		print "\t\tQuantity: " + Validate(str(ingredient["amount"]))
		print "\t\tMeasurement: " + Validate(ingredient["unit"])
		print "\t\tDescriptor: " + Validate(ingredient["descriptor"])
		print "\t\tPreparation: " + Validate(ingredient["preparation"])
		print "\t\tPreparation description: " + Validate(ingredient["preparationDescription"])

	print "\nPRIMARY COOKING METHOD: " + Validate(primaryMethod)

	print "\nMETHODS: " + Validate(", ".join(methods))

	print "\nTOOLS: " + Validate(", ".join(tools))

	print "\nDIRECTIONS:"
	for s, step in enumerate(parsedDirections):
		print "\tStep " + str(s+1) + ": "
		print "\t\tIngredients: " + Validate(", ".join(step["ingredients"]))
		print "\t\tMethods: " + Validate(", ".join(step["methods"]))
		print "\t\tTools: " + Validate(", ".join(step["tools"]))
		print "\t\tTimes: " + Validate(", ".join(step["times"]))
		print "\t\tDirection: " + step["text"]


if __name__ == '__main__':
	main()