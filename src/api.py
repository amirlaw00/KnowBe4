#Master File that contains methods allowing API acces to various KB4 endpoints
import requests

import csv

#Key -> Name, Value -> Set of admin Emails.  Used in AccountInfo.
OrgNadmin = {}
#Key -> API Key, Value -> Name of the Org. Used in AccountInfo and for console debugging
KeyNName = {}
#Key -> Console Name, Value -> Innactive Users. Used in Main
InnactiveUsers = {}

'''Grabs a count of all users in a given console.'''
#Input: API Key for a given KB4 account
#Output: Number of users in the console
#Delivers output as a return value, could be refactored to print out to a file or console
def UserCount(key): #Grabs all users for given account key, and returns a count of how many users are in this console
    pullUsers = "https://us.api.knowbe4.com/v1/users"
    page = 1
    user_count = 0

    while True:
        r = requests.get(pullUsers, params={"status": "active", "per_page": 500, "page": page}, headers={"Authorization": "Bearer " + key})
        if r.status_code != 200:
            print("Can't grab users: " + key)
            print(r.reason)
            print(r.status_code)
            print(r.text)
            return user_count

        Users = r.json()
        if not Users:  # If Users is an empty list, we've reached the end of the pages
            break

        user_count += len(Users)
        page += 1
    return user_count

'''Grabs a count of all campaigns in a given console, this is a combination of training and phishing campaigns'''
#Input: API Key for a given KB4 account
#Output: Number of campaigns in the console
#Delivers output as a return value, could be refactored to print out to a file or console
def CampaignCount(key):
    pullTrainingCampaigns = "https://us.api.knowbe4.com/v1/training/campaigns"
    pullPhishingCampaigns = "https://us.api.knowbe4.com/v1/phishing/campaigns"

    r = requests.get(pullTrainingCampaigns, headers={"Authorization": "Bearer " + key})
    if r.status_code != 200:
        print("Can't grab training campaigns: " + key)
        print(r.reason)
        return
    TrainingCampaigns = r.json()

    r = requests.get(pullPhishingCampaigns, headers={"Authorization": "Bearer " + key})
    if r.status_code != 200:
        print("Can't grab phishing campaigns: " + key)
        print(r.reason)
        return
    PhishingCampaigns = r.json()

    #return a count of how many campaigns have been run in this console
    return len(TrainingCampaigns) + len(PhishingCampaigns)

'''Grabs general KB4 account info for given account key.'''
#Input: API Key for a given KB4 account
#Output: Name of the console, and a set of admin emails for this console
#Delivers output as a return value, could be refactored to print out to a file or console

#Note: Also helps populate the OrgNadmin and KeyNName dictionaries
def AccountInfo(key): 

    #Grabs all account info
    pullAccount = "https://us.api.knowbe4.com/v1/account"
    r = requests.get(pullAccount, headers={"Authorization": "Bearer " + key})
    if r.status_code != 200:
        print("Can't grab account info: " + key)
        print(r.reason)
        return
    Account = r.json()
    
    #print(r.status_code)

    if 'name' not in Account.keys():
        #Print out that this account has no name
        print("No Name: " + key)

    Name = Account['name'] #Grabs the name of the console
    AdminEmails = set() #Creates set that will be used to fill OrgNAdmin 
    AdminSet = Account['admins']
    for user in AdminSet:
        AdminEmails.add(user['email'])
    OrgNadmin[Name] = AdminEmails
    KeyNName[key] = Name
    return Name, AdminEmails

'''
Grabs training data for given account key.  Prints out the console name along with a list of all training modules 
and the number of users enrolled in each module. Could be used to gauge the effectiveness of training modules.
'''
#Input: API Key for a given KB4 account
#Output: List of training modules and the number of users enrolled in each module
#Delivers output to the output file created in main, this is due to the size of output that would be generated
def TrainingData(key): #Grabs training data for given account key
    pullTrainings = "https://us.api.knowbe4.com/v1/training/enrollments"
    r = requests.get(pullTrainings, headers={"Authorization": "Bearer " + key})
    TrainingData = r.json()

    if r.status_code != 200:
        print("Can't grab training data: " + key)
        print(r.reason)
        return 

    Modules = set()
    for enrollment in TrainingData:
        Modules.add(enrollment['module_name'])
    

    ModCount = {}

    for module in Modules:
        count = 0
        for enrollment in TrainingData:
            if enrollment['module_name'] == module:
                count += 1
        ModCount[module] = count

    #prints to the output file opened in main
    output.write(KeyNName[key] + "\n")
    output.write(str(ModCount) + "\n") #Could be refactored to print out in a more readable format
    output.write("\n")
    output.write("\n")
    output.write("\n")
    #print(KeyNName[key])
    #print(ModCount)

'''
Leverages the "NCDPI Innactive User Group" naming convention to grab the number of innactive users in a given console
Could be edited to notify if account does not have an innactive user group
'''
#Input: API Key for a given KB4 account
#Output: Number of innactive users in the console
#Delivers output as a return value, could be refactored to print out to a file or console
def PullInnactive(key):
    # Write a function that calls this api (https://us.api.knowbe4.com/v1/groups), and grabs the NCDPI Innactive Group data related to key
    
    pullGroups = "https://us.api.knowbe4.com/v1/groups"
    page = 1
    member_count = 0
    while True:
        r = requests.get(pullGroups, headers={"Authorization": "Bearer " + key}, params={"page": page, "per_page": 500})
        if r.status_code != 200:
            print("Can't grab group data: " + key)
            print(r.reason)
            print(r.status_code)
            print(r.text)
            return member_count

        Groups = r.json()
        if not Groups:  # If Groups is an empty list, we've reached the end of the pages
            break

        # Search group data for a group that contains the word "NCDPI".  Based on our "NCDPI Innactive User Group" naming convention
        for group in Groups:
            if "ncdpi" in group['name'].lower():
                # If found, add the group member_count to member_count
                member_count += group['member_count']

        page += 1

    InnactiveUsers[KeyNName[key]] = member_count 

    #name = KeyNName[key]  #Uncomment to do any console printing of the information if you want
    
    return member_count

# Main method
if __name__ == "__main__":
    "Feel free to un-comment the following code to utilize different methods depending on what you're trying to accomplish."
    
    #List that will contain psu number and the corresponding api.  Could be optimized to only contain the api key, since PSU number is never used in this script.
    Keys = []

    #Prints out the total number of Reporting API Keys that we have access to, based on keys.csv
    with open('../auth/keys.csv', 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            Keys.append(row)
        print("Total number of keys:" + str(csvreader.line_num))

    #An output file that will be used to summarize the training data of each psu
    output = open("../data/PSUAccountSummary.txt", "a") #FKA "PSUTrainingData.txt"


    for key in Keys:
        AccountInfo(key[1]) #Uncomment this line to gather account info of this psu
        TrainingData(key[1]) #Uncomment this line to gather training data of this psu
        #PullInnactive(key[1]) #Uncomment this line to gather innactive user data of this psu

        #Print out a progress update to the console
        print("Progress: " + str(Keys.index(key)) + "/" + str(len(Keys)))

    output.close()

    #sort PullInnactive by descending value
    InnactiveUsers = dict(sorted(InnactiveUsers.items(), key=lambda item: item[1], reverse=True))

    #Print the contents of the InnactiveUsers dictionary in the format "Console Name: Innactive Users" to a file
    output = open("PSUInnactiveUsers.txt", "w")
    for key in InnactiveUsers:
        output.write(key + ": " + str(InnactiveUsers[key]) + " Innactive Users\n")
    output.close()


'''
    At this point, all emails should be in the set and dictionary below.  Along with that, you have dictionary access to
    every key, organizaiton, and admins for each or.  Access however you'd like
'''

    #print(AllEmails)
    #print(OrgNadmin)







