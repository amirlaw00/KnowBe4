import sys
import csv
import KB4Keys as grab_keys

KB4_PSU = grab_keys.main() #Dictionary that ties each api key in KB4 to it's relevant lea_number
#Print out the total number of keys, use for sanity check with current amount of orgs in KB4
print("Total number of keys:" + str(len(KB4_PSU)))

#Export values of KB4_PSU to a csv file
with open('../auth/keys.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    for key in KB4_PSU:
        csvwriter.writerow([key, KB4_PSU[key]])



#print(str(len(KB4_PSU)) + ' PSUs in KnowBe4')