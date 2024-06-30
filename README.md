this work is inspired by GDSC@APU's APSpace Timetable Automation workshop presented by JPChong  
link to recording here https://youtu.be/YpdT6wfD6_E?si=_NUVGkj2SwrGVds3

To set up the Python script and automation workflow locally on your device,  
please follow the instructions in the attached PDF and recording from the link above

The section onwards are the instructions to set up the automation via GitHub actions
after committing your script to GitHub
prepare a requirements.txt in the root folder and paste in these dependencies to allow the workflow to import the necessary libraries

    requests==2.25.1
    beautifulsoup4==4.9.3
    google-api-python-client==2.11.0
    google-auth==1.30.0
    google-auth-oauthlib==0.4.6
    google-auth-httplib2==0.1.0

next go to your repository settings > security > secrets and variables,  
and set up your repository secrets (not environment secrets),  
by clicking "new repository secret",  
this is to access the environment variables that the workflow would otherwise require dotenv and read cred.env to access (I changed to using this method for added security)

optional  
to make it more secure, encode your service_account JSON with base64 and add it as a repository secret as well,  
you can do that by copy-pasting your entire JSON and converting it with this converter: https://www.base64encode.org/

next, set up your automation,  
click on your repository Actions and click on "set up a workflow yourself"  
then paste in this yaml text (do read the comments for explanations)  

    name: Weekly Timetable Update #the workflow name
    
    on:
      schedule:
        - cron: '0 0 * * 0'                      #Runs every Saturday at midnight UTC(cron syntax)
      workflow_dispatch:                         #to manually test it
    
    jobs:
      run-script:
        runs-on: ubuntu-latest                  #run using ubuntu
    
        steps:
        - name: Checkout code                  #switch to the current release
          uses: actions/checkout@v4
    
        - name: Set up Python                  #set up python to run the script
          uses: actions/setup-python@v5
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

lastly, to modify the Python script
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


since we don't need dotenv anymore we can remove that, we also need to use os instead of os.path.

we can also remove these lines that use dotenv

    current_directory = os.path.dirname(__file__)
    env_file_path = os.path.join(current_directory, 'cred.env')
    load_dotenv(env_file_path)

and lastly, for the b64 encoded service_account JSON, change the get_credentials function to this

    def get_credentials(SCOPES):
        # Decode the base64 encoded service account JSON from the environment variable
        service_account_info = json.loads(base64.b64decode(os.getenv('SERVICE_ACCOUNT')))
        creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        return creds

you can also delete the files service_account.json and cred.env if you still have them.  
that should be all the changes.
