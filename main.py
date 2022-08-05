import csv

import usaddress

cityPropertyTax = []


def PropertyTaxLookup(city):
    global cityPropertyTax
    cityname = city.lower()

    for dict in cityPropertyTax:
        if cityname in dict:
            # print("This city's property tax is: " + dict.get(cityname))
            return dict.get(cityname)

    return "na"


with open("PropTax.csv") as csvFile:
    reader = csv.reader(csvFile)
    next(reader, None)  # skip the headers
    data_read = [row for row in reader]

    for row in data_read:
        tempDict = {
            row[0].lower(): row[4],
        }
        cityPropertyTax.append(tempDict)

for cityTax in cityPropertyTax:
    print(cityTax)

with open("data.csv") as csvFile:
    reader = csv.reader(csvFile)
    next(reader, None)  # skip the headers
    data_read = [row for row in reader]

    listings = []
    for row in data_read:
        location = usaddress.parse(row[11])

        cityIndex = 0
        i = 0
        for data in location:
            if "PlaceName" in data:
                cityIndex = i
                break
            i += 1

        cityName = location[i][0].replace(',', '')

        tempDict = {
            "address": row[11],
            "url": row[5],
            "price": int(row[10]),
            "zestimate": int(row[28]) if (len(row[28]) > 0) else "na",
            "rentZestimate": float((row[60])) if (len(row[60]) > 0) else "na",
            "beds": float(len(row[52])) if (len(row[52]) > 0) else "na",
            "baths": float(row[51]),
            "sqft": row[72],
            "propertyTax": PropertyTaxLookup(cityName),
        }

        listings.append(tempDict)
        print(tempDict)

        # print("address " + row[11])
        # print("price " + float(row[10]))
        # print("zestimate " + float(row[28]))
        # print("rentZestimate " + float(row[60]))
        # print("beds " + float(row[52]))
        # print("baths " + float(row[51]))
        # print("sqft " + row[72])

# completedListings have all info needed to calculate cap rate
completedListings = []
for listing in listings:
    # print (listing)
    repairCost = 0
    closingCost = (0.02 * listing["price"]) + (0.03 * listing["price"])
    totalCost = listing["price"] + closingCost + repairCost
    totalCostReduced10 = (0.9 * listing["price"]) + closingCost + repairCost
    totalCostReduced15 = (0.85 * listing["price"]) + closingCost + repairCost
    totalCash = listing["price"] + closingCost + repairCost - (listing["price"] * 0.8)

    # --------------------------------- Expenses -----------------------------------------
    rentableUnits = 1  # ASSUMPTION
    insurance = 950 * rentableUnits  # rentableUnits is number of units assuming most will be single family
    capExpense = 1000 * rentableUnits
    cleaningMaintenance = 400 * rentableUnits
    Administration = 100 * rentableUnits

    if listing["propertyTax"] != "na":
        totalExpenses = insurance + capExpense + cleaningMaintenance + Administration + float(listing["propertyTax"])
        listing["totalExpenses"] = totalExpenses
    else:
        print("Missing property tax for: " + listing["address"])
        continue

    # --------------------------------- Expenses -----------------------------------------
    unleveragedOperatingIncome = (listing["rentZestimate"] * 11) - totalExpenses  # multiplying by 11 for vacancy loss
    listing["unleveragedOperatingIncome"] = unleveragedOperatingIncome
    print("unleveragedOperatingIncome")
    print(unleveragedOperatingIncome)
    print(r"(listing[\"rentZestimate\"] * 11) ")
    print("rentZestimate")
    print(listing["rentZestimate"])
    print((listing["rentZestimate"] * 11) )
    print("unleveragedOperatingIncome")
    print(unleveragedOperatingIncome)
    capRate = unleveragedOperatingIncome / totalCost
    capRateReduced10 = unleveragedOperatingIncome / totalCostReduced10
    capRateReduced15 = unleveragedOperatingIncome / totalCostReduced15
    # print(unleveragedOperatingIncome)
    # print(totalCost)
    # print(capRate)

    listing["capRate"] = capRate
    listing["capRateReduced10"] = capRateReduced10
    listing["capRateReduced15"] = capRateReduced15
    completedListings.append(listing)

print("The list printed sorting by capRate: ")
sortedCompletedListings = sorted(completedListings, key=lambda i: i['capRate'], reverse=True)

try:
    with open('output.csv', 'w', newline='') as csvFile:
        writer = csv.writer(csvFile, delimiter=',', )
        writer.writerow(["address", "url", "cap rate", "cap rate with 10% reduced purchase price", "cap rate with 15% "
                "reduced purchase price", "price", "zestimate", "rentZestimate", "beds", "baths", "totalExpenses",
                         "Unleveraged Operating Income"])
        for listing in sortedCompletedListings:

            writer.writerow([listing['address'], listing["url"], str(round(listing["capRate"], 5)),
                             str(round(listing["capRateReduced10"], 5)), str(round(listing["capRateReduced15"], 5)),
                             listing["price"], listing["zestimate"],
                             listing["rentZestimate"], listing["beds"], listing["baths"], listing["totalExpenses"],
                             listing["unleveragedOperatingIncome"]])
            # print(listing["url"])
            # print("Cap Rate:\t" + str(round(listing["capRate"], 5)))
            # print("Price:\t" + str(listing["price"]))


        for listings1 in listings:
            if listings1["propertyTax"] != "na":
                totalExpenses = insurance + capExpense + cleaningMaintenance + Administration + float(
                    listing["propertyTax"])
                listing["totalExpenses"] = totalExpenses
            else:
                writer.writerow([listings1['address'], listings1["url"], "Missing property tax data"])
                continue
except Exception as e:
    print(e)