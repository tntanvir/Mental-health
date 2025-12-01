# api/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone
User = get_user_model()
from notifications.utils import send_notification



@shared_task(bind=True)
def push_notification(self):
    now = timezone.now().time().replace(second=0, microsecond=0)

    users = User.objects.filter(checking_time=now)
    print('chaking',now)
    for user in users:
        print("Matched user:", user.email)
        send_notification(user,'Daily Check-in Notification')
    return f"Found {users.count()} users"
    
    
