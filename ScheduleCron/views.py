import logging
import socket
import os
from datetime import datetime
from django.shortcuts import render

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from Auth.views import TokenHasScopeForMethod
from Company.models import Company
from Question.serializers import getLastWorkshopJoin
from Users.models import User, UserProfile
from EmailPostLearningContent.models import EmailPostContent
from MailMagazine.models import MailMagazine
from Workshop.models import UserWorkshop

def LogCronjobErrors(message):
    path_access_log = os.getenv('PATH_ERROR_CRONJOB_LOG', '')
    logging.basicConfig(filename=path_access_log + 'error_cron_job.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.ERROR)

    logging.info(message)


def DailyEmailMagazine(user,weekday_mail):
    key_value = weekday_mail.split(',')
    key = key_value[0]
    WEB_CLIENT = os.getenv('WEB_CLIENT')
    context = {
        'full_name': user.last_name + ' ' +  user.first_name,
        'url_setting': WEB_CLIENT + '/mail-magazine-setting',
        'url_email_magazine': WEB_CLIENT + '/mail-magazine-article/'+str(key),
    }
    email_html_message = render_to_string('daily_email_magazine/content.html', context)
    msg = EmailMultiAlternatives(
        # title:
        ("【3分間コーチ】3 Minutes Tips（vol." + key + "）"),
        # message:
        email_html_message,
        # from:
        "coacha_3mins@coacha.com",
        # to:
        [user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()

def FirstSendEmailMagazine(user,weekday_mail):
    key_value = weekday_mail.split(',')
    key = key_value[0]
    WEB_CLIENT = os.getenv('WEB_CLIENT')
    context = {
        'full_name': user.last_name + ' ' + user.first_name,
        'url_setting': WEB_CLIENT + '/mail-magazine-setting',
        'url_email_magazine': WEB_CLIENT + '/mail-magazine-article/' + str(key),
    }
    email_html_message = render_to_string('first_daily_email_magazine/content.html', context)
    msg = EmailMultiAlternatives(
        # title:
        ("【3分間コーチ】3 Minutes Tips（vol." + key + "）"),
        # message:
        email_html_message,
        # from:
        "coacha_3mins@coacha.com",
        # to:
        [user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


def LastSendEmailMagazine(user,weekday_mail):
    key_value = weekday_mail.split(',')
    key = key_value[0]
    WEB_CLIENT = os.getenv('WEB_CLIENT')
    context = {
        'full_name': user.last_name + ' ' + user.first_name,
        'url_setting': WEB_CLIENT + '/mail-magazine-setting',
        'url_email_magazine': WEB_CLIENT + '/mail-magazine-article/' + str(key),
    }
    email_html_message = render_to_string('last_daily_email_magazine/content.html', context)
    msg = EmailMultiAlternatives(
        # title:
        ("【3分間コーチ】3 Minutes Tips（vol." + key + "）"),
        # message:
        email_html_message,
        # from:
        "coacha_3mins@coacha.com",
        # to:
        [user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


class RunCronjobMailMagazine(GenericAPIView):
    throttle_classes = ()
    permission_classes = [TokenHasScopeForMethod]
    authentication_classes = [OAuth2Authentication]
    required_scopes_per_method = {'GET': ['coacha_admin']}

    def get(self, request, *args, **kwargs):
        users = User.objects.filter(is_superuser=False).all()
        for user in users:
            try:
                is_send_email = user.userprofile.is_send_email
                if is_send_email is True:
                    weekday_today = datetime.today().weekday()
                    today = datetime.now()
                    strDate = today.strftime("%Y-%m-%d")
                    weekday_step = 0
                    # We check today is Tuesday or Thursday
                    if weekday_today == 1 or weekday_today == 3:
                        cronjob_mail_magazine = user.getCronjobMailMagazine()
                        if cronjob_mail_magazine is not False:
                            date_start = cronjob_mail_magazine[1]
                            date_start = datetime.strptime(date_start, "%Y-%m-%d")
                            today = today.strptime(strDate, "%Y-%m-%d")
                            weekday_step = int(cronjob_mail_magazine[0])
                            weekday_step = weekday_step + 1
                            if weekday_step <= 26 and today != date_start:
                                weekday_mail = str(weekday_step) + ','+strDate
                            else:
                                continue
                        else:
                            weekday_mail = '0,'+ strDate

                        # SAVE KEY VALUE
                        user.cronjob_mail_magazine = weekday_mail
                        user.save()

                        #count user request email
                        self.update_list_mail_magazine_count(user)

                        #send email
                        if weekday_step == 26:
                            LastSendEmailMagazine(user, weekday_mail)
                        elif weekday_step == 0:
                            FirstSendEmailMagazine(user, weekday_mail)
                        else:
                            DailyEmailMagazine(user,weekday_mail)

            except UserProfile.DoesNotExist:
                message = "ERROR log at {}".format({
                    'user_id': user.id,
                    'workshop_id': 'profile does not exist',
                })
                LogCronjobErrors(message)
        return Response({"data": 'OK', 'code': 200})

    def update_list_mail_magazine_count(self, user):
        try:
            email_post_content = EmailPostContent.objects.get(user=user)
            current_count = email_post_content.count_send_email
            email_post_content.count_send_email = current_count + 1
        except EmailPostContent.DoesNotExist:
            email_post_content = EmailPostContent.objects.create(user=user)
            email_post_content.count_send_email = 1
        email_post_content.save()

run_cronjob_mail_magazine = RunCronjobMailMagazine.as_view()