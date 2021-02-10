from django.contrib import admin
from .models import Board , Topic , Post , Profile , Star , Staff

admin.site.register(Board)
admin.site.register(Topic)
admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Star)
admin.site.register(Staff)