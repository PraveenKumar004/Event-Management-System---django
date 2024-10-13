from django.db import models

class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    full_details = models.TextField()
    poster = models.ImageField(upload_to='posters/')
    date = models.DateField()
    location = models.CharField(max_length=255)
    total_tickets = models.IntegerField()
    questions = models.JSONField()
    user_id = models.IntegerField()

    class Meta:
        db_table = 'event' 
        managed = False  

    def __str__(self):
        return self.name 
