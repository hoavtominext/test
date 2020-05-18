from django.db import models

from Users.models import User


class EmailPostContent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count_send_email = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "email_post_content"
