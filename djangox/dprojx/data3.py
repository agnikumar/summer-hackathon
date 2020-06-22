#!/usr/bin/env python

"""
    Script to import data from .csv file to Model Database DJango
    To execute this script run: 
                                1) manage.py shell
                                2) exec(open('file_name.py').read())
"""

import csv
import sys
from dappx.models import RecTransaction
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

csvs = ['yelp_network_data.csv']      # Csv file path  
csv.field_size_limit(sys.maxsize)


for path in csvs:
  with open(path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    count = 0
    for row in reader:
      with open(path, newline='') as csvfile:
        try:
          if count > 0:
            trans = RecTransaction.objects.create(business_id=row[0], name=row[1], address=row[2], city=row[3], state=row[4], postal_code=row[5], latitude=row[6], longitude=row[7], stars=row[8], review_count=row[9], categories=row[12], review_id=row[14], user_id=row[15], review_stars=row[16], text=row[20], friends=row[22])
            trans.save()
            print(count)
          count += 1
        except Exception as e:
          pass