from django.db import models
from django.utils import timezone
from model_utils import Choices
from django.contrib.auth.models import User


class Board(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=100)
    num_stars = models.IntegerField(null=True,default=0)

    def __str__(self):
        return self.name

class Topic(models.Model):
    subject = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board,on_delete = models.CASCADE, related_name='topics')
    starter = models.ForeignKey(User,on_delete = models.CASCADE, related_name='topics')


class Post(models.Model):
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic,on_delete = models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User,on_delete = models.CASCADE, related_name='posts')
    updated_by = models.ForeignKey(User,on_delete = models.CASCADE, null=True, related_name='+')

class Profile(models.Model):
    empid = models.CharField(max_length=15,primary_key=True,default='00000')
    name = models.CharField(max_length=30,default='ชื่อเล่น')
    position = models.CharField(max_length=20,default='ตำแหน่ง') #Position
    position_level = models.CharField(max_length=5,default='ระดับ') #LevelCode
    department_name = models.CharField(max_length=50,default='สังกัด') #DepartmentShort
    department_code = models.CharField(max_length=50,default='รหัสSAP') #NewOrganizationalCode
    workage = models.DateField(auto_now_add=False,null=True,default=timezone.now) #StaffDate - วันปัจจุบัน

class Star(models.Model):
    comment = models.TextField()
    point = models.IntegerField(null=True,default=0)
    yollow_card = models.IntegerField(null=True,default=0)
    date = models.DateField(auto_now_add=True,null=True)
    status = models.CharField(max_length=20,default='Progress')

class Staff(models.Model):
    profile = models.ForeignKey(Profile,on_delete= models.CASCADE)
    star = models.ForeignKey(Star,on_delete= models.CASCADE)