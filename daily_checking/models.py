from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class DailyChecking(models.Model):
    FEELING_CHOICES = (
        ("Awful 😫", "Awful 😫"),           
        ("Sad 😢", "Sad 😢"),               
        ("Slightly Off 😕", "Slightly Off 😕"),  
        ("Stressed 😣", "Stressed 😣"),     
        ("Anxious 😰", "Anxious 😰"),       
        ("Tired 😴", "Tired 😴"),           
        ("Neutral 😐", "Neutral 😐"),       
        ("Calm 😌", "Calm 😌"),             
        ("Happy 😄", "Happy 😄"),           
        ("Excited 🤩", "Excited 🤩"),       
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_checkings')
    feeling = models.CharField(max_length=50, choices=FEELING_CHOICES)
    question = models.TextField(blank=True)
    answer = models.TextField()
    index = models.IntegerField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.get_feeling_display()} - {self.created_at.date()}"
    def save(self, *args, **kwargs):
        self.index = [key for key, _ in self.FEELING_CHOICES].index(self.feeling)+1
        super().save(*args, **kwargs)
