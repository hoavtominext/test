import os
from crontab import CronTab

my_cron = CronTab(True)
DOMAIN_API = os.getenv('API_ENDPOINT')
http_link = str('curl -s ') + str('https://api.test.3mins.coacha.com') + str('/v1/schedule-cron/run-cronjob-mail-magazine')
job = my_cron.new(command=http_link)
job.every().day()
my_cron.write()