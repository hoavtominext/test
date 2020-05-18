import os
from crontab import CronTab
from dotenv import load_dotenv
import sys
import requests
my_cron = CronTab(True)



dotenv_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/DjangoRestApi/.env'
load_dotenv(dotenv_path)

API_ENDPOINT = os.getenv('API_ENDPOINT')
WEB_CLIENT = os.getenv('WEB_CLIENT')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
DOMAIN_API = os.environ.get('API_ENDPOINT')

username = sys.argv[1]
password = sys.argv[2]

data = {'username': username,'password': password,}
r = requests.post(API_ENDPOINT + '/v1/auth/login-admin', data=data)
data = r.json()

token = data['data']['access_token']
bearer = data['data']['token_type']

headers = {
    'content-type': 'application/x-www-form-urlencoded',
    'Authorization' : bearer+' '+token
}

request = requests.get(API_ENDPOINT + '/v1/schedule-cron/run-cronjob-mail-magazine', data={}, headers=headers)
