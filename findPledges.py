#! /usr/bin/env python
# -*- coding: UTF-8 -*-

import wiki
import api

#TODO
#Get list of current pledges

def strike_stripper(pledger):
    print(pledger)
    if "</s>" not in pledger:
        return pledger
    elif "</s>" in pledger:
        index = pledger.index("</s>")
        return pledger[:index]

def pledge(input_data):
    return pledger(input_data)
    
class pledger(object):
    '''
    '''
    def __init__(self, input_data):
        input_data = input_data.replace(" ","")
        input_data = input_data[1:]
        self.amount, self.name = input_data.split("--")
        if self.amount[0:3] == "<s>": #Only takes off first <s>, need to take </s> 
            self.amount = float(self.amount[5:])
            self.paid = True
        else:
            self.amount = float(self.amount[2:])
            self.paid = False
        self.name = strike_stripper(self.name)
        self.name = self.name.decode("utf-8")
        print(input_data, self.amount, self.name, self.paid)
        
def value_maker(amount):
    if amount == "?":
        return amount
    else:
        return float(amount)

def value_getter(string):
    string = string.split(":")[1].split("'")
    for i in string:
        if i != "" and i != " ":
            return value_maker(i[2:])

def parse_pledges(lines):
    found = False
    finish = False
    summary = False
    pledgers = []
    for i in lines:
        if found == False:
            if i == "==Pledges==":
                found = True
        elif finish == False:
            if i == "":
                finish = True
            else:
                pledgers.append(i)

        elif finish and found == True:
            if i.split(":")[0].lower() == "running total":
                total = value_getter(i)

            if i.split(":")[0].lower() == "approximate target":
                target = value_getter(i)

            if i.split(":")[0].lower() == "paid":
                paid = value_getter(i)

    return {"pledgers":pledgers, "total":total, "target":target, "paid":paid}


def find_info(site):
    exclude = [] # pages to exclude
    # create a Wiki object
    site = wiki.Wiki(site) 
    #params = {'action':'query', 'title':'Main Page',"prop":"revisions","format":"xml","rvprop":"content"}
    params = {'action':'query','list':'allpages','apprefix':'Pledges'}
    request = api.APIRequest(site, params)
    result = request.query()
    pledges = []
    for i in result["query"]["allpages"]:
        print(i["title"])
        pledges.append(i["title"])

    parsed_data = []
   
    for pledgename in pledges:
        params = {'action':'query','rvprop':'content','prop':'revisions|categories',"format":"xml","titles":"%s" %\
        pledgename}
        request = api.APIRequest(site,params)
        result = request.query()
        result = result["query"]["pages"].values()
        print(pledgename)
        try:
            if result[0]["categories"][0]["title"].lower() == "category:completedpledge":
                print("Pledge Completed")
            elif result[0]["categories"][0]["title"].lower() == "category:pledge":
                print("Pledge not completed.")
                result = result[0]["revisions"][0]["*"]
                result = result.encode("utf-8")
                lines = result.split("\n")
                
                parsed = parse_pledges(lines)
                parsed["title"] = pledgename
                parsed_data.append(parsed)
                
        except KeyError:
            print("Not a pledge")

    
    report = open("report.txt", "w")
    for i in parsed_data:
        print(i["title"],i["total"],i["target"],i["paid"])
        i["pledgers"] = map(pledge, i["pledgers"])
        report.write("\n"+i["title"]+"\n")
        if type(i["target"]) == str:
            pass
        else:
            if i["total"] >= i["target"]:
                report.write("Pledge met!\n")
                report.write("Current Non-Payers:\n")
                for pledger in i["pledgers"]:
                    if pledger.paid == False:
                        print(str(pledger.amount))
                        print(pledger.name)
                        out_string = pledger.name + u" £" + str(pledger.amount) + "\n"
                        report.write(out_string.encode("utf-8"))
            else:    
                report.write("Pledge not met. \nAmount left until total: " + str(i["target"]-i["total"]) +"\n")
                report.write("Current Pledgers:\n")
                for pledger in i["pledgers"]:
                    print(str(pledger.amount))
                    print(pledger.name)
                    out_string = pledger.name + u" £" + str(pledger.amount) + "\n"
                    report.write(out_string.encode("utf-8"))

    report.close()

find_info("http://wiki.london.hackspace.org.uk/w/api.php")

