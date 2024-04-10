# KnowBe4 API Modules & Scripts

A collection of scripts leveraging the KnowBe4 Reporting API.
Official KnowBe4 Reporting Documentation can be found [here](https://developer.knowbe4.com/).

### Prerequisites
The scripts require that you have a multi-tenant management account in KnowBe4 along with a list of every console's reporting API token.

If you'd like to take advantage of this script you will need at the very least a file called *Keys.csv* in the /auth folder.  This file would need the following structure: [PSU Code],[API Key]
### Keys.csv
```
305,LMMWHMNi9NjLxLnxNCMaCuOH9kqVLwTE
371,xSj5naapMeEPMvMqpPi1upYCKEvP81WG
640,FyLyF8ELB9RfwpA6OoQfum4vCNISEr93
651,V5G18Lc4EpBneHdTJ2Ier4IN2d5IU7jR
614,zEtt7Vo29hyqgkfMJRxE9FqHynQCTlF1
```

If you use, 1Password to store your console API keys, you can use **ExportKeys.py** to generate your own *Keys.csv* file.  Please put your *export.json* file from 1Password in /auth.

## api.py
This file serves two purposes.
- Holds methods that allow easy access to various KnowBe4 api endpoints based on a single API key.  Specifically getting user info, campaign information, account information, training information, and inactive users
- Sets the stage for larger operations that require the use of numerous apis.

Please note that certain methods are custom-built with our specific infrastructure in place.  Please follow the code comments to understand where to make applicable changes to your organization.


## activeonboarding.py
This file is an example of a larger script that leverages methods in **api.py** along with outside data from EDDIE and our onboarding form to figure out which consoles in our organization are inactive. 

If you'd like to run **activeonboarding.py** on your own district, please also include an active charter school report from the NCDPI EDDIE system, a list of currently onboarded contact emails, and a list of related PSU codes in your /input folder

Please make appropriate changes to input files in the code relevant to your console.
