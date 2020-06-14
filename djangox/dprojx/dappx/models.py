from django.db import models
from django.contrib.auth.models import User

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

def __str__(self):
  return self.user.username