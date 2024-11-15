from django.db import models
from django.utils.timezone import now

class EventUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=200)

    class Meta:
        db_table = 'user'
        managed = False

    def __str__(self):
        return self.username


class OTP(models.Model):
    username = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = 'OTP'
        managed = False

    def __str__(self):
        return f"{self.username} - {self.otp}"
