# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Frequency(models.Model):
    fqnum = models.AutoField(db_column='fqNum', primary_key=True)  # Field name made lowercase.
    usertype = models.CharField(db_column='userType', max_length=100, blank=True, null=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userId', blank=True, null=True)  # Field name made lowercase.
    total = models.IntegerField(blank=True, null=True)
    safe = models.IntegerField(blank=True, null=True)
    danger = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Frequency'


class Myphoto(models.Model):
    mpnum = models.AutoField(db_column='mpNum', primary_key=True)  # Field name made lowercase.
    userid = models.ForeignKey('User', models.DO_NOTHING, db_column='userId', blank=True, null=True)  # Field name made lowercase.
    filename = models.CharField(db_column='fileName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    image = models.CharField(db_column='Image', max_length=255, blank=True, null=True)  # Field name made lowercase.
    filevolume = models.IntegerField(db_column='fileVolume', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MyPhoto'


class User(models.Model):
    userid = models.CharField(db_column='userId', primary_key=True, max_length=100)  # Field name made lowercase.
    userpassword = models.CharField(db_column='userPassword', max_length=100, blank=True, null=True)  # Field name made lowercase.
    username = models.CharField(db_column='userName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    useremail = models.CharField(db_column='userEmail', max_length=100, blank=True, null=True)  # Field name made lowercase.
    userclass1 = models.IntegerField(db_column='userClass1', blank=True, null=True)  # Field name made lowercase.
    userclass2 = models.IntegerField(db_column='userClass2', blank=True, null=True)  # Field name made lowercase.
    socialuser = models.IntegerField(db_column='socialUser', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'User'
