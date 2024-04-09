
import sys, csv, os

# Get the grandparent directory
grandparent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Append the grandparent directory to sys.path
sys.path.append(grandparent_dir)

from KnowBe4 import api
#UserCount, CampaignCount, PullInnactive, AccountInfo
from operator import itemgetter


def ProcessKeys(csv_file_path):
    output = []

    # Open the CSV file
    with open(csv_file_path, "r") as file:
        # Create a CSV reader object
        reader = csv.reader(file)
        
        # Iterate through each line in the CSV file
        for i, row in enumerate(reader):
            # Get the key from the 2nd column of the line
            key = row[1]
            LEA = row[0]
            
            # Get the user count for the key
            user_count = api.UserCount(key)
            name, admin_emails = api.AccountInfo(key)
            
            # Remove any admin emails that contain "ncdpi".  Based on our service account model "ncdpi-kb4-admin@[psudomainhere].edu"
            admin_emails = [email for email in admin_emails if "ncdpi" not in email.lower()]

            if len(admin_emails) == 0:
                admin_emails = "N/A"
            
            # Call PullInnactive from API, and subtract that from user_count to get active users
            inactive_users = api.PullInnactive(key)
            if inactive_users is None:
                inactive_users = 0

            inactive_users = int(inactive_users)
            active_users = user_count - inactive_users

            # If user_count is < 11, add to output with campaign count as "N/A"
            if active_users < 11:
                output.append({"LEA": LEA, "Name": name, "User Count": active_users, "Total Campaign Count": "N/A", "Admin Emails": admin_emails, "Status": "LOW USERS"})
            else:
                # Get the total campaign count for the key
                total_campaign_count = api.CampaignCount(key)
                
                # If total_campaign_count is < 6, add to output
                if total_campaign_count < 6:
                    output.append({"LEA": LEA, "Name": name, "User Count": active_users, "Total Campaign Count": total_campaign_count, "Admin Emails": admin_emails, "Status": "LOW CAMPAIGNS"})
                
                # Print a progress update every 25 lines
                if (i + 1) % 2 == 0:
                    print(f"Processed {i + 1} lines.")
                
        # Print a final progress update
        print(f"Processed all lines.")
        
    # Sort the output based on user count and then campaign count, from highest to lowest
    sorted_output = sorted(output, key=itemgetter("User Count", "Total Campaign Count"), reverse=True)

    # Write the sorted output to the file
    with open("ListOfConsoles.csv", "w") as output_file:
        for item in sorted_output:
            output_file.write(f"LEA: {item['LEA']}, Name: {item['Name']}, User Count: {item['User Count']}, Total Campaign Count: {item['Total Campaign Count']}, {item['Status']}, Admin Emails: {item['Admin Emails']}\n")
            
            # Print a progress update every 25 lines
            if (i + 1) % 2 == 0:
                print(f"Wrote {i + 1} lines.")

def SpotCheck(consoles_file_path, onboarding_emails_file_path, onboarding_codes_file_path):
    consoles = []
    onboarding_emails = []
    
    # Open the onboarding emails file and put all of the emails into a list
    with open(onboarding_emails_file_path, "r") as onboarding_file:
        for line in onboarding_file:
            onboarding_emails.append(line.strip().lower())

    # Open the onboarding codes file and put all of the codes into a list
    with open(onboarding_codes_file_path, "r") as onboarding_codes_file:
        onboarding_codes = [line.strip() for line in onboarding_codes_file]

    # Open the consoles file and put all of the rows into a list
    with open(consoles_file_path, "r") as consoles_file:
        for line in consoles_file:
            consoles.append(line.strip())

    # Create a new file that will contain the subset of rows that don't have an admin email match in the onboarding emails file
    excluded_consoles = 0
    with open("O/FinalConsoleList.csv", "w", newline='') as spotcheck_file:
        writer = csv.writer(spotcheck_file)
        for line in consoles:
            columns = line.split(",", maxsplit=5)
            # Grab the names from the 2nd column
            name = columns[1].replace("Name: ", "").strip()
            lea_code = columns[0].replace("LEA: ", "").strip()
            admin_emails = columns[-1].replace("Admin Emails: ", "").strip().strip("[]").replace("'", "").split(", ")

            if not any(email in onboarding_emails for email in admin_emails) and lea_code not in onboarding_codes:
                writer.writerow(columns)
            else:
                excluded_consoles += 1
                print("Excluded console: " + name)
    # Close the files
    onboarding_file.close()
    consoles_file.close()
    spotcheck_file.close()
    onboarding_codes_file.close()

    # Print out the number of rows that were not included in the SpotCheckedConsoles file
    print("Number of consoles already started onboarding: " + str(excluded_consoles))
    

def match_and_update(batch_file, charter_file, output_file):
    batch_data = []

    with open(batch_file, 'r') as file:
        for line in file:
            row = line.strip().split(',', maxsplit=5)
            batch_data.append(row)

    # Read the charter school report into a list of dictionaries
    with open(charter_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header
        charter_data = [{ 'LEA': row[1], 'Email': row[-1] } for row in reader]

    # IF a charter school in the batch file is in the charter school report, update the batch file with the email from the report
    for batch_row in batch_data:
        for charter_row in charter_data:
            if batch_row[0].replace("LEA: ", "").strip(" '") == charter_row['LEA'].strip(" '"):
                # Extract the existing emails
                if "N/A" in batch_row[-1]:
                    existing_emails = []
                    new_email = charter_row['Email'].strip('"')
                    batch_row[-1] = "Admin Emails: ['" + new_email + "']"
                else:
                    existing_emails = batch_row[-1][len("Admin Emails: ['"):-2].split("', '")
                    # Append the new email if it's not a duplicate
                    new_email = charter_row['Email'].strip('"')
                    if new_email not in existing_emails:
                        existing_emails.append(new_email)
                    # Update the 'Admin Emails' field
                    batch_row[-1] = batch_row[-1][:len("Admin Emails: ['")] + "', '".join(existing_emails) + batch_row[-1][-2:]

    # Write the updated data to the output file
    with open(output_file, 'w') as f:
        for data_row in batch_data:
            f.write(', '.join(data_row) + '\n')

# Function to strip the emails from the batch file
def StripEmails(input_file, output_file):
    with open(input_file, 'r') as csv_file, open(output_file, 'w') as txt_file:
        for line in csv_file:
            columns = line.split(",", maxsplit=5)
            emails = columns[-1].replace("Admin Emails: ", "").strip().strip("[]").replace("'", "").split(", ")
            for email in emails:
                if email != "N/A":
                    txt_file.write(email + "\n")
    #close the files
    csv_file.close()
    txt_file.close()

if __name__ == "__main__":
    #Uncomment the function you want to run

    #Run ProcessKeys when you want to get a list of consoles that have less than 11 users or less than 6 campaigns based on the keys in the keys.csv file
    #Keys.csv is a file that contains the api keys for each organization in the format "LEA Code, API Key"
    #ProcessKeys("keys.csv")

    #Run MatchAndUpdate when you want to add the EDDIE charter school admin emails to the main list of consoels
    #Active_charter_schools_report.csv is a file that contains the charter school admin emails in the format "LEA Code, Charter School Name, Charter School Admin Email". Comes from EDDIE
    match_and_update('O/ListOfConsoles.csv', "O/active_charter_schools_report.csv", "O/UpdatedConsoleList.csv")

    #Run SpotCheck when you want to make sure that the consoles you are sending emails to are not already in the onboarding process
    SpotCheck("O/UpdatedConsoleList.csv", "O/OnboardingEmails.txt","O/OnboardingLEACode.txt")  #Onboarding emails is a list of emails form the onbdoarding form

    #Run StripEmails when you are ready to send out the email blast to a subset of consoles
    #StripEmails("O/UpdatedBatch.csv", "ActiveOnboardingEmails.txt")