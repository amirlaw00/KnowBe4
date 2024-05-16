import json
import os

#Returns a list of all KB4 API Reporting Keys that are generated from a 1Password Report
def main():

    #Open the 1Password Report
    keys = dict()

    # Get the directory of the current script file
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Join the directory with the filename
    file_path = os.path.join(script_dir, '../auth/export.json')

    # Open the file
    with open(file_path, encoding="utf8") as one_password:
        data = json.load(one_password)

        # Get the list of vaults
        vaults = data['accounts'][0]['vaults']

        # Find the vault with the name "KnowBe4-NCDPI" and get its items
        LEA_list = next((vault['items'] for vault in vaults if vault['attrs']['name'] == 'KnowBe4-NCDPI'), None)
        #LEA_list = data['accounts'][0]['vaults'][1]['items']

        for LEA in LEA_list:
            name = LEA['overview']['title']
            name = name.lstrip()  # Remove leading spaces
            if (len(name) < 5 or name[4] != '-') and not name.startswith('KIPP'):  # Skips irrelevant items in list, except those starting with 'KIPP'
                # print out the invalid names
                print(name + ': invalid name \n')
                #print(LEA)  # Print out the entire item for debugging
                continue
            
            LEA_Number = name[0:3]

            Token = str()


            sections = LEA['details']['sections']
            for section in sections:
                fields =  section['fields']
                for field in fields:
                    try:
                        if field['title'] == 'Reporting API Token':
                            Token = field['value']['concealed']
                            break
                    except:
                        print(name + ': no API found \n')
                else:
                    continue
                break

            keys[LEA_Number] = Token
        
        return keys

#run main() if this file is run directly
if __name__ == "__main__":
    main()