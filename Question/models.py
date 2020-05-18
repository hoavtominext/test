from django.db import models

CATEGORY = (
    ('A.日常の関わり', 'A.日常の関わり'),
    ('B.対話力', 'B.対話力')
)
TYPE = (
    ('個別対応', '個別対応'),
    ('前進', '前進'),
    ('傾聴', '傾聴'),
    ('継続', '継続'),
    ('質問', '質問'),
    ('目的共有', '目的共有'),
)


# Create your models here.
class Questions(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(choices=CATEGORY, max_length=20)
    type = models.CharField(choices=TYPE, max_length=20)
    factor = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "questions"
