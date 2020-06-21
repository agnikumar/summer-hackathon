from django.db import models
from django.contrib.auth.models import User
from django_mysql.models import ListCharField

# Create your models here.

class UserProfileInfo(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  type_choices = [("CL", "Client"), ("CO", "Contractor")]
  user_type = models.CharField(
        max_length=2,
        choices=type_choices,
        default=type_choices[0][0],
  )
  
  def get_type(self):
    return self.user_type

class Transaction(models.Model):
  client = models.CharField(max_length=80)
  contractor = models.CharField(max_length=80)
  payment = models.IntegerField()
  date = models.DateField()

class Contractor(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=80)
  business_id = models.CharField(max_length=80)
  address = models.CharField(max_length=80)
  city = models.CharField(max_length=80)
  state = models.CharField(max_length=2)
  postal_code = models.IntegerField()
  stars = models.FloatField()
  review_count = models.IntegerField()
  categories = ListCharField(base_field=models.CharField(max_length=80), max_length=80)

  @classmethod
  def create(cls, user=None, name=None, business_id=None, address=None, city=None, state=None, postal_code=None, stars=0, review_count=0, categories=[]):
    contractor = cls(user=user, name=name, business_id=business_id, address=address, city=city, state=state, postal_code=postal_code, stars=stars, review_count=review_count, categories=categories)
    return contractor


class Client(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=80)
  city = models.CharField(max_length=80)
  state = models.CharField(max_length=2)
  postal_code = models.IntegerField()
  friends = ListCharField(base_field=models.CharField(max_length=80), max_length=1000)  

  @classmethod
  def create(cls, user=None, name=None, business_id=None, address=None, city=None, state=None, postal_code=None, stars=0, review_count=0, categories=[]):
    client = cls(user=user, name=name, city=city, state=state, postal_code=postal_code, friends=friends)
    return client

  class Meta:
    permissions = (("is_client", "can view the payments and friends tab"),)

def __str__(self):
  return self.user.username