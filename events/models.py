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
    paid = models.BooleanField()
    amount = models.IntegerField()
    total_collection = models.IntegerField()
    winner = models.TextField()

    class Meta:
        db_table = 'event' 
        managed = False  

    def __str__(self):
        return self.name 
    
class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    ticket_id = models.CharField(max_length=255)
    answers = models.TextField()  
    participation = models.BooleanField(default=False)
    winner = models.BooleanField(default=False)

    class Meta:
        db_table = 'event_registration'
        unique_together = ('event', 'user_id')
        managed = False 
    
    def __str__(self):
        return self.event.name
