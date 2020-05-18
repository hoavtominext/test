from django.conf.urls import url
from .views import questions_list, questions_import, answer_questions, send_email_complete_questions, \
    history_result_answer_question, pre_assessment_check

urlpatterns = [
    url(r'list', questions_list, name="questions_list"),
    url(r'^import-csv', questions_import, name="questions_import"),
    url(r'^answer-questions', answer_questions, name="questions_import"),
    url(r'^send-email-complete-questions', send_email_complete_questions, name="send_email_complete_questions"),
    url(r'^history-result-answer-question', history_result_answer_question, name="history_result_answer_question"),
    url(r'^pre-assessment-check', pre_assessment_check, name="pre_assessment_check"),


]