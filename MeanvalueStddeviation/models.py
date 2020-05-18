from django.db import models

# Create your models here.
TYPE = (
    ('個別対応', '個別対応'),
    ('前進', '前進'),
    ('傾聴', '傾聴'),
    ('継続', '継続'),
    ('質問', '質問'),
    ('目的共有', '目的共有'),
    ('全体', '全体'),
)


# Create your models here.
class MeanvalueStddeviation(models.Model):
    type = models.CharField(choices=TYPE, max_length=20)
    average_value = models.FloatField(max_length=25)
    standard_deviation = models.FloatField(max_length=25)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "meanvalue_stddeviation"
