from django.db.models.signals import post_save  # This is a Signal That get to fired after an object is saved.
from django.contrib.auth.models import User  # Built In User Model. It is going to send the signal.
from django.dispatch import receiver  # It is a function that gets this signal and then perform some task.

# Redundant signal removed and consolidated into auction/models.py
