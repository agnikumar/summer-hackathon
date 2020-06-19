#!/usr/bin/env python

"""
    Script to import data from .csv file to Model Database DJango
    To execute this script run: 
                                1) manage.py shell
                                2) exec(open('file_name.py').read())
"""

import csv
from dappx.models import Contractor 
from django.contrib.auth.models import User, Group, Permission

csvs = ['contractor_data.csv']      # Csv file path  

for path in csvs:
  with open(path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    with open(path, newline='') as csvfile:
      spamreader = csv.reader(csvfile)
      count = 0
      for row in spamreader:
        if count > 0:
          group, created = Group.objects.get_or_create(name='Contractor')
          user = User(username="contractor"+str(count))
          user.set_password("test")
          user.save()
          user.groups.add(group)
          contractor = Contractor.create(user=user, name=row[0], business_id=row[1], address=row[2], city=row[3], state=row[4], postal_code=int(row[5]), stars = float(row[6]), review_count = int(float(row[7])), categories=row[8].split(","))
          contractor.save()
          print(count)
          if count == 25:
            break
        count += 1