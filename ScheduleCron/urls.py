from django.conf.urls import url
from .views import run_cronjob_mail_magazine

app_name = 'run_schedule_cron_send_email_post'
urlpatterns = [
    # ex: /workshop/
    url(r'^run-cronjob-mail-magazine', run_cronjob_mail_magazine, name="run_cronjob_mail_magazine"),
]
