import numpy
from django.core.mail import EmailMultiAlternatives

from django.db import models
from django.db.models import Count
from django.template.loader import render_to_string

from MeanvalueStddeviation.models import MeanvalueStddeviation
from Question.models import Questions
from Users.models import User
from Users.serializers import WEB_CLIENT
from Workshop.models import Workshop,UserWorkshop
from Company.models import Company
from MeanvalueStddeviation import constant
from scipy.stats import norm
from operator import itemgetter
from datetime import datetime, timedelta

def SendEmailAfterCompleteQuestion(admin_name, user, result):
    # send an e-mail to the user
    score_listen = result.score_listen  # Điểm lắng nghe
    score_ask_questions = result.score_ask_questions  # Điểm đặt câu hỏi
    score_advance = result.score_advance  # Điểm Advance score
    score_retention = result.score_retention  # Điểm duy trì
    score_sharing_purpose = result.score_sharing_purpose  # Điểm chia sẻ mục đích
    score_personal_reciprocal = result.score_personal_reciprocal  # Điểm chia sẻ mục đích
    total_normdist_score = result.total_normdist_score  # Diem tong da tinh normdist_score
    workshop = result.workshop
    context = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'admin_name': admin_name,
        'score_listen': score_listen,
        'score_ask_questions': score_ask_questions,
        'score_advance': score_advance,
        'score_retention': score_retention,
        'score_sharing_purpose': score_sharing_purpose,
        'score_personal_reciprocal': score_personal_reciprocal,
        'total_normdist_score': total_normdist_score,
        'url': WEB_CLIENT + "/consequence"
    }

    # render email text
    email_html_message = render_to_string('complete-questions/content.html', context)
    msg = EmailMultiAlternatives(
        # title:
        ("Result Seminar {title}-{date}".format(title="today",date=workshop.date_workshop)),
        # message:
        email_html_message,
        # from:
        "noreply@somehost.local",
        # to:
        [user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


def distAnswers(user_id, count_assessment):
    answers = []
    querysetAnswer = Answer.objects.filter(user_id=user_id, count_assessment=count_assessment)
    for answer in querysetAnswer:
        data = {
            'id': answer.question_id,
            'factor': answer.point,
            'name': answer.question.name
        }
        answers.append(data)
    dictAnswers = sorted(answers, key=itemgetter('id'), reverse=True)

    return dictAnswers


# Create your models here.
class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, null=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, default=1)
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='Workshop', null=False, default=1)
    count_assessment = models.IntegerField(default=1)
    point = models.IntegerField(null=False, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "answer"
        unique_together = ('user', 'question', 'workshop','company', 'count_assessment')


class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, null=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=False, default=1)
    count_assessment = models.FloatField(default=1)
    score_listen = models.FloatField(null=True)  # Điểm lắng nghe
    score_ask_questions = models.FloatField(null=True)  # Điểm đặt câu hỏi
    score_advance = models.FloatField(null=True)  # Điểm Advance score
    score_retention = models.FloatField(null=True)  # Điểm duy trì
    score_sharing_purpose = models.FloatField(null=True)  # Điểm chia sẻ mục đích
    score_personal_reciprocal = models.FloatField(null=True)  # Điểm chia sẻ mục đích
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    '''
        Điểm tổng hợp	=　Average(Điểm lắng nghe、Điểm đặt câu hỏi、 Advance score 、Điểm duy trì、Điểm chia sẻ mục đích、Điểm đối ứng cá nhân)
        =　Average(4.25456150922978 , 5.26894537745070 , 4.83184840555306 , 4.50656905579928 , 5.41515016962705 , 4.42350985764725)
        =　4.78343072921785
    '''

    total_average_score = models.FloatField(null=True)  # Điểm tổng hợp

    '''
    Độ hài long tổng hợp　=　NORMDIST( Điểm tổng hợp của A , Giá trị trung bình tổng hợp , Độ lệch chuẩn tổng hợp , TRUE) * 100
	                      =　NORMDIST(4.78343072921785 , 4.52520593911527 , 0.690956009974255 , TRUE) * 100
	                      =　64.5694060347197
    '''
    total_normdist_score = models.FloatField(null=True)  # Độ hài long tổng hợp

    class Meta:
        db_table = "result"
        unique_together = ('user', 'workshop','company', 'count_assessment')


def scoreAnswerAdvance(user_id,company_id,workshop_id, count_assessment):
    answers_advance = Answer.objects.filter(question__type__contains=constant.ADVANCE, user_id=user_id, company_id=company_id,workshop_id=workshop_id,
                                            count_assessment=count_assessment)
    total_score = 0
    for answer in answers_advance:
        point = answer.point * answer.question.factor
        total_score = total_score + point
    return total_score


def scoreAnswerListen(user_id,company_id,workshop_id, count_assessment):
    answers_listen = Answer.objects.filter(question__type__contains=constant.LISTENT, user_id=user_id, company_id=company_id,workshop_id=workshop_id,
                                           count_assessment=count_assessment)
    total_score = 0
    for answer in answers_listen:
        point = (answer.point * answer.question.factor)
        total_score = total_score + point

    return total_score


def scoreAnswerAskQuestion(user_id,company_id,workshop_id, count_assessment):
    answers_ask_question = Answer.objects.filter(question__type__contains=constant.ASK_QUESTION, user_id=user_id, company_id=company_id,workshop_id=workshop_id,
                                                 count_assessment=count_assessment)
    total_score = 0
    for answer in answers_ask_question:
        point = answer.point * answer.question.factor
        total_score = total_score + point
    return total_score


def scoreAnswerRetention(user_id,company_id,workshop_id, count_assessment):
    answers_retention = Answer.objects.filter(question__type__contains=constant.RETENTION, user_id=user_id, company_id=company_id,workshop_id=workshop_id,
                                              count_assessment=count_assessment)
    total_score = 0
    for answer in answers_retention:
        point = answer.point * answer.question.factor
        total_score = total_score + point
    return total_score


def scoreAnswerSharingPurpose(user_id,company_id,workshop_id, count_assessment):
    sharing_purpose = Answer.objects.filter(question__type__contains=constant.SHARING_PURPOSE, user_id=user_id, company_id=company_id,workshop_id=workshop_id,
                                            count_assessment=count_assessment)
    total_score = 0
    for answer in sharing_purpose:
        point = answer.point * answer.question.factor
        total_score = total_score + point
    return total_score


def scoreAnswerPersonalReciprocall(user_id,company_id,workshop_id, count_assessment):
    personal_reciprocal = Answer.objects.filter(question__type__contains=constant.PERSONAL_RECIPROCAL, user_id=user_id, company_id=company_id,workshop_id=workshop_id,
                                                count_assessment=count_assessment)
    total_score = 0
    for answer in personal_reciprocal:
        point = answer.point * answer.question.factor
        total_score = total_score + point
    return total_score


def totalAverageScore(user_id,company_id,workshop_id, count_assessment, score_listen=0, score_ask_questions=0, score_advance=0,
                      score_retention=0,
                      score_sharing_purpose=0, score_personal_reciprocal=0):
    if score_listen == 0 and score_ask_questions == 0 and score_advance == 0 and score_retention == 0 and score_sharing_purpose == 0 and score_personal_reciprocal == 0:
        score_listen = scoreAnswerListen(user_id,company_id,workshop_id, count_assessment)
        score_ask_questions = scoreAnswerAskQuestion(user_id,company_id,workshop_id, count_assessment)
        score_advance = scoreAnswerAdvance(user_id,company_id,workshop_id, count_assessment)
        score_retention = scoreAnswerRetention(user_id,company_id,workshop_id, count_assessment)
        score_sharing_purpose = scoreAnswerSharingPurpose(user_id,company_id,workshop_id, count_assessment)
        score_personal_reciprocal = scoreAnswerPersonalReciprocall(user_id,company_id,workshop_id, count_assessment)

    data = [score_listen, score_ask_questions,
            score_advance, score_retention,
            score_sharing_purpose, score_personal_reciprocal]
    average = numpy.mean(data)
    return average


def totalNormdistScoreWithType(val, type):
    meanvalue_stddeviation = MeanvalueStddeviation.objects.filter(type=type)[:1].get()
    return norm.cdf(val, meanvalue_stddeviation.average_value, meanvalue_stddeviation.standard_deviation) * 100

def countWorkshopCompany(company_id):
    count_workshop_company = Workshop.objects \
        .filter(company_id=company_id, ).count()

    return count_workshop_company

def totalNormdistScoreTotal(val):
    meanvalue_stddeviation = MeanvalueStddeviation.objects.filter(type='全体')[:1].get()
    return norm.cdf(val, meanvalue_stddeviation.average_value, meanvalue_stddeviation.standard_deviation) * 100

def numberPeoplePreAssessment(company_id):
    number_people_pre_assessment = UserWorkshop.objects \
        .distinct().values('user_id').annotate(user_count=Count('user_id')) \
        .filter(company_id=company_id, ).count()

    if number_people_pre_assessment is None:
        return 0
    return number_people_pre_assessment

def numberPeopleCompleted(company_id):
    number_people_completed = Result.objects \
        .distinct().values('user_id').annotate(user_count=Count('user_id')) \
        .filter(company_id=company_id, ).count()

    return number_people_completed


def numberPeopleCompletedThisMonth(company_id,workshop):
    workshop_date = workshop.date_workshop
    end_date = workshop_date + timedelta(days=30)
    start_date = workshop_date
    number_people_completed_month = Result.objects \
        .distinct().values('user_id').annotate(user_count=Count('user_id')) \
        .filter(count_assessment__gte=2, created_at__range=(start_date, end_date),
                company_id=company_id).count()

    return number_people_completed_month


def numberPeopleCompletedSecondMonth(company_id,workshop):
    workshop_date = workshop.date_workshop
    end_date = workshop_date + timedelta(days=90)
    start_date = workshop_date
    number_people_completed_second_month = Result.objects \
        .distinct().values('user_id').annotate(user_count=Count('user_id')) \
        .filter(count_assessment__gte=2, created_at__range=(start_date, end_date),
                company_id=company_id).count()

    return number_people_completed_second_month


def numberPeopleCompletedThreeMonth(company_id,workshop):
    workshop_date = workshop.date_workshop
    end_date = workshop_date + timedelta(days=120)
    start_date = workshop_date
    number_people_completed_second_month = Result.objects \
        .distinct().values('user_id').annotate(user_count=Count('user_id')) \
        .filter(count_assessment__gte=2, created_at__range=(start_date, end_date),
                company_id=company_id).count()

    return number_people_completed_second_month
