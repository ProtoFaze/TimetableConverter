this work is inspired from GDSC GDSC APSpace Timetable Automation workshop presented by JPChong
link to recording here https://youtu.be/YpdT6wfD6_E?si=_NUVGkj2SwrGVds3

To setup the python script and automation workflow locally on your device please follow instructions in the attached pdf

Below is the instructions to setup the automation via github workflows
after saving your script in github
prepare a requirements.txt in the root folder and paste in these dependencies to allow the workflow to import the necessary libraries
--start--
requests==2.25.1
beautifulsoup4==4.9.3
google-api-python-client==2.11.0
google-auth==1.30.0
google-auth-oauthlib==0.4.6
google-auth-httplib2==0.1.0
--end--

next go to your repository settings>security>secrets and variables, 
and set up your repository secrets (not environment secrets), 
by clicking new repository secret, 
this is to access the environment variables that the workflow would otherwise require dotenv and read cred.env to access (i changed to using this method for added security)

optional
to make it more secure, encode your service_account json with base64 and add it as a repository secret as well, 
you can do that by copy pasting your entire json and converting it with this converter: https://www.base64encode.org/

next, set up your automation, 
click on your repository Actions and click on "set up a workflow yourself"
then paste in this yaml text (do read the comments for explanations)
--start--
name: Weekly Timetable Update #the workflow name

on:
  schedule:
    - cron: '0 0 * * 0'                      #Runs every Saturday at midnight UTC(cron syntax)
  workflow_dispatch:                         #to manually test it

jobs:
  run-script:
    runs-on: ubuntu-latest                  #run using ubuntu

    steps:
    - name: Checkout code                  #read the codebase
      uses: actions/checkout@v2

    - name: Set up Python                  #set up python to run the script
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies          #install the dependencies specified in requirements.txt
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run timetable script          #run the python script
      env:
        SENDER: ${{ secrets.SENDER }}
        PASSWORD: ${{ secrets.PASSWORD }}
        RECEIVER: ${{ secrets.RECEIVER }}
        SERVICE_ACCOUNT: ${{ secrets.SERVICE_ACCOUNT }}  #this line is optional if you converted your service_account.json into a repo secret
      run: python timetable_converter.py      
--end--

lastly, to modify the python script
if you followed the pdf or recording, this is the immediate modification after the file is completely coded according to the workshop, if not, do refer to those materials

from datetime import  datetime, timedelta, date
import requests
from bs4 import BeautifulSoup

from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
import smtplib,ssl
from email.message import EmailMessage

#optional if using b64 encoded service account
import json
import base64

since we dont need dotenv anymore we can remove that, we also need to use os instead of os.path.

we can also remove these lines 

current_directory = os.path.dirname(__file__)
env_file_path = os.path.join(current_directory, 'cred.env')
load_dotenv(env_file_path)

and lastly, for the b64 encoded service_account json, change get credentials to this
def get_credentials(SCOPES):
    # Decode the base64 encoded service account JSON from the environment variable
    service_account_info = json.loads(base64.b64decode(os.getenv('SERVICE_ACCOUNT')))
    creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    return creds

that should be all the changes.
