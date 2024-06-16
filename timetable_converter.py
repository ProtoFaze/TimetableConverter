from datetime import  datetime, timedelta, date
import requests
from bs4 import BeautifulSoup

from googleapiclient.discovery import build
from google.oauth2 import service_account
import os.path
from dotenv import load_dotenv
import smtplib,ssl
from email.message import EmailMessage

current_directory = os.path.dirname(__file__)
env_file_path = os.path.join(current_directory, 'cred.env')
load_dotenv(env_file_path)

class Email:
    def __init__(self):
        self.sender = os.getenv('SENDER')
        self.password = os.getenv('PASSWORD')
        self.receiver = os.getenv('RECEIVER')
        self.subject = "Your weekly APU Timetable"

    def send_email(self, html_content):
        context = ssl.create_default_context()
        em = EmailMessage()
        em['From'] = self.sender
        em['To'] = self.receiver
        em['Subject'] = self.subject
        em.set_content(html_content, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(self.sender, self.password)
            smtp.sendmail(self.sender, self.receiver, em.as_string())

def get_week_start(): 
    today = date.today()
    days_until_next_week = 7 - today.weekday()
    next_week_start = today + timedelta(days=days_until_next_week)
    return next_week_start

def fetch_time_table(week, intake, intake_group):
    response = requests.get(f'https://api.apiit.edu.my/timetable-print/index.php?Week={week}&Intake={intake}&Intake_Group={intake_group}&print_request=print_tt')
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.find('table', class_ = 'table')
    
def get_credentials(SCOPES):
    SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__) ,'service_account.json')
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes = SCOPES)
    return creds

def create_event(service,entry):
    date_str = entry['Date']
    time_str = entry['Time']

    date = datetime.strptime(date_str, '%a, %d-%b-%Y')
    start_time_str, end_time_str = time_str.split(' - ')
    start_time = datetime.strptime(start_time_str, '%H:%M')
    end_time = datetime.strptime(end_time_str, '%H:%M')
    start_datetime = date.replace(hour = start_time.hour, minute = start_time.minute)
    end_datetime = date.replace(hour = end_time.hour, minute = end_time.minute)

    start_isoformat = start_datetime.isoformat()
    end_isoformat = end_datetime.isoformat()
    time_zone = 'Asia/Kuala_Lumpur'

    event = {
        'summary': f"{entry['Subject/Module']}",
        'location': f"{entry['Classroom']}",
        'start':{
            'dateTime': f"{start_isoformat}",
            'timeZone': f"{time_zone}"
        },
        'end':{
            'dateTime': f"{end_isoformat}",
            'timeZone': f"{time_zone}"
        }
        }
    
    return service.events().insert(calendarId = 'damonngkhaiweng@gmail.com', body = event).execute()
    

def main():
    intake='APU2F2311CS(AI)'
    intake_group='All'
    remove_list = ['MAE']
    week_start = get_week_start()

    timetable_table = fetch_time_table(week_start, intake, intake_group)
    if timetable_table:
        timetable_data = []

        rows = timetable_table.find_all('tr')[2:]

        if rows:
            for row in rows:
                cell = row.find_all('td')

                date = cell[0].text.strip()
                time = cell[1].text.strip()
                classroom = cell[2].text.strip()
                location = cell[3].text.strip()
                subject = cell[4].text.strip()
                lecturer = cell[5].text.strip()

                module_name = subject.split('-')[3]

                if module_name not in remove_list:
                    timetable_data.append({
                        'Date': date,
                        'Time': time,
                        'Classroom': classroom,
                        'Location': location,
                        'Subject/Module': subject,
                        'Lecturer': lecturer
                    }) 
        SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = get_credentials(SCOPES)
        service = build('calendar', 'v3', credentials=creds) 
        for entry in timetable_data:
            create_event(service, entry)

        calendar_link = f"https://calendar.google.com/calendar/u/0/r/week/{week_start.year}/{week_start.month}/{week_start.day}"
        html_content = f"""
<html>
    <body>
        <p>Your apu timetable for the week of {week_start} is ready</p>
        <p>Please find calendar with the link below:</p>
        <p>Link:{calendar_link}</p>
    </body>
</html>
"""
        email_client = Email()
        title = f"export complete"
        email_client.send_email(html_content)
        print(title)
    else:
        html_content = f"""
            <html>
                <body>
                    <p>Hi, there is no class schedule for week {week_start}</p>
                </body>
            </html>
            """
        email_client = Email()
        title = f"No class in this week!"
        email_client.send_email(html_content)
        print(title)


if __name__ == "__main__":
    main()