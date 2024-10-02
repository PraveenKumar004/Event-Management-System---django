from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=200)

    class Meta:
        db_table = 'user'
        managed = False

    def __str__(self):
        return self.username
