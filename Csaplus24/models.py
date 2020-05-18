from django.db import models
from Question.models import Questions

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


def distCsaplus24Average():
    querysetCsaplus24Average = Csaplus24Average.objects.filter()
    csaplus_averages = []
    for csaplus_average in querysetCsaplus24Average:
        data = {
            'id': csaplus_average.id.id,
            'factor': csaplus_average.factor,
            'name': csaplus_average.name
        }
        csaplus_averages.append(data)

    return csaplus_averages


# Create your models here.
class Csaplus24Average(models.Model):
    id = models.OneToOneField(
        Questions,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    name = models.CharField(max_length=255)
    category = models.CharField(choices=CATEGORY, max_length=20)
    type = models.CharField(choices=TYPE, max_length=20)
    factor = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "csaplus24_average"


# Create your models here.
class Csaplus24Coefficient(models.Model):
    id = models.OneToOneField(
        Questions,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    name = models.CharField(max_length=255)
    category = models.CharField(choices=CATEGORY, max_length=20)
    type = models.CharField(choices=TYPE, max_length=20)
    factor = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "csaplus24_coefficient"
