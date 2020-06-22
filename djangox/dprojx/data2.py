#!/usr/bin/env python

"""
    Script to import data from .csv file to Model Database DJango
    To execute this script run: 
                                1) manage.py shell
                                2) exec(open('file_name.py').read())
"""

import csv
from dappx.models import Client
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

csvs = ['client_data.csv']      # Csv file path  

for path in csvs:
  with open(path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    count = 0
    for row in reader:
      with open(path, newline='') as csvfile:
        if count > 0:
          print(row)
          content_type = ContentType.objects.get_for_model(Client)
          permission = Permission.objects.get(content_type=content_type, codename='is_client')
          group, created = Group.objects.get_or_create(name='Client')
          group.permissions.add(permission)
          user = User(username=row[0])
          user.set_password("test")
          user.save()
          user.groups.add(group)
          client = Client.objects.create(user=user, name=row[0], uid=row[1], city=row[2], state=row[3], postal_code=int(row[4]), friends=row[5].split(","))
          client.save()
          print(count)
        count += 1
