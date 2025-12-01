from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True)

    
    # New Fields
    PLAN_CHOICES = (
        ('Free', 'Free'),
        ('Pro', 'Pro'),
        ('Premium', 'Premium'),
    )
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='Free')
    profile_done = models.IntegerField(default=0)
    current_feel = models.CharField(max_length=100, blank=True, null=True)
    notifications = models.BooleanField(default=True)
    current_stack = models.IntegerField(default=0)
    last_stack_date = models.DateField(blank=True, null=True)
    total_checking = models.IntegerField(default=0)
    checking_time = models.TimeField(blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_create = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    avarage = models.IntegerField(default=0)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.update_profile_completion()
        self.checking_time = self.checking_time.replace(second=0, microsecond=0)
        self.avarage = self.total_checking / 10
        super().save(*args, **kwargs)

    def update_profile_completion(self):
        total_fields = 4
        filled_fields = 0
        
        if self.name and self.name != "New User":
            filled_fields += 1
        if self.gender:
            filled_fields += 1
        if self.country:
            filled_fields += 1
        if self.image:
            filled_fields += 1
            
        self.profile_done = int((filled_fields / total_fields) * 100)

        

    def generate_otp(self):
        import random
        otp = str(random.randint(100000, 999999))
        self.otp = otp
        self.otp_create = timezone.now()
        self.save()
        return otp

    def is_otp_valid(self, otp):
        if self.otp != otp:
            return False
        
        if not self.otp_create:
            return False

        # Check if OTP is expired (5 minutes)
        time_difference = timezone.now() - self.otp_create
        if time_difference.total_seconds() > 300: # 5 minutes * 60 seconds
            return False
            
        return True
