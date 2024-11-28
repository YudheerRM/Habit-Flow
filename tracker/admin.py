from django.contrib import admin
from .models import Habit, ProgressLog
# Register your models here.
admin.site.register(Habit)
admin.site.register(ProgressLog)