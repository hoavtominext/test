from datetime import datetime

from django.core.validators import validate_ipv4_address, validate_ipv6_address
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError


def ip_validator(ip):
    try:
        validate_ipv4_address(ip)
    except ValidationError:
        try:
            validate_ipv6_address(ip)
        except ValidationError:
            raise ValidationError('Invalid IP address')

# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=255,null=False)
    date_contract_start = models.DateTimeField(null=False,default=datetime.now)
    date_contract_end = models.DateTimeField(null=False,default=datetime.now)
    remark = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "company"  # your existing mysql table name

class CompanyIpList(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, related_name='ip_list', null=True)
    ip_address = models.CharField('IP Address', max_length=15, validators=[ip_validator] )

    class Meta:
        db_table = "companyiplist"
        unique_together = ['company', 'ip_address']