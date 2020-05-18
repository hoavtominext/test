from django.conf.urls import url
from .views import UsersList, detail_user, UserCreate, UserUpdate, UserDelete,UserImport,ChangePasswordView,setting_send_email_user,forgot_password_request,forgot_password_confirm_request,\
    remove_list_user,send_email_request_user,check_login,admin_forgot_password,de_active_user,active_user,check_admin_login,check_supper_admin_login,count_user,UserExport

app_name = "users"

urlpatterns = [
    url(r'^$', UsersList.as_view(), name="users_list"),
    url(r'^create', UserCreate.as_view(), name="user_create"),
    url(r'^delete-list/$', remove_list_user, name="remove_list_user"),
    url(r'^send-email-request-user/$', send_email_request_user, name="send_email_request_user"),

    url(r'(?P<pk>\d+)/detail/$', detail_user, name="user_detail"),
    url(r'(?P<pk>\d+)/update/$', UserUpdate.as_view(), name="user_update"),
    url(r'(?P<pk>\d+)/delete/$', UserDelete.as_view(), name="user_delete"),
    url(r'^export-csv', UserExport.as_view(), name="user_export"),
    url(r'^import-csv', UserImport.as_view(), name="user_import"),
    url(r'^change-password', ChangePasswordView.as_view(), name="change-password"),
    url(r'^setting-send-email-user', setting_send_email_user, name="setting_send_email_user"),
    url(r'^forgot-password/$', forgot_password_request, name="forgot_password_request"),
    url(r'^admin-forgot-password/$', admin_forgot_password, name="admin_forgot_password"),
    url(r'^forgot-password/confirm/$', forgot_password_confirm_request, name="forgot_password_confirm_request"),
    url(r'^deactive-user/$', de_active_user, name="de_active_user"),
    url(r'^active-user/$', active_user, name="active_user"),
    url(r'^check_login/$', check_login, name="check_login"),
    url(r'^check_admin_login/$', check_admin_login, name="check_admin_login"),
    url(r'^check_supper_admin_login/$', check_supper_admin_login, name="check_supper_admin_login"),
    url(r'^count-user/$', count_user, name="count_user"),

]