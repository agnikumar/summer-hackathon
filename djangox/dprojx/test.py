#!/usr/bin/env python
from dappx.models import Contractor

all_entries = Contractor.objects.all()
print(all_entries)
print(all_entries.values())
