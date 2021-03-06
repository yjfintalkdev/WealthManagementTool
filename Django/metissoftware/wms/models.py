from datetime import datetime
from django.core.urlresolvers import reverse
from django.db import models
from django.forms import ModelForm, TextInput
from django.core.validators import RegexValidator
from bootstrap3_datetime.widgets import DateTimePicker
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)

class FAUserManager(BaseUserManager):
    def create_user(self, email, first_name, surname,
                    dob, ni_number, password, **extra_fields):
        if not email:
            raise ValueError('users must have an email address')
        if not first_name:
            raise ValueError('users must have a first name')
        if not surname:
            raise ValueError('users must have a surname')
        if not dob:
            raise ValueError('users must have a dob')
        if not ni_number:
            raise ValueError('users must have a national insurance number')

        user = self.model(email=email, first_name=first_name,
                          surname=surname, dob=dob, ni_number=ni_number)

        user.set_password(password)
        user.is_staff = False
        user.is_active = True
        user.is_superuser = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, surname,
                         dob, ni_number, password, **extra_fields):

        user = self.create_user(email, first_name, surname, dob,
                                ni_number, password, **extra_fields)

        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class FA(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=64, unique=True)
    first_name = models.CharField(max_length=64, default="**DEFAULT**")
    middle_name = models.CharField(max_length=64, blank=True)
    surname = models.CharField(max_length=64, default="**DEFAULT**")
    image = models.ImageField(upload_to='fa_images', default='/media/person-placeholder.png')
    dob = models.DateField(default="1990-01-01")
    ni_regex = RegexValidator(regex=r'^(?!BG)(?!GB)(?!NK)(?!KN)(?!TN)(?!NT)(?!ZZ)(?:[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z])(?:\s*\d\s*){6}([A-D]|\s)$', message="Must be in the format: 'AA999999A', restrictions to characters apply'")
    ni_number = models.CharField(
        max_length=9, validators=[ni_regex], primary_key=True)
    is_staff=models.BooleanField(default=False)
    is_admin=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'surname', 'dob', 'ni_number', 'is_active']

    def get_full_name(self):
        return "%s" % self.email

    def get_short_name(self):
        return "%s" % self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    objects = FAUserManager()




class Client(models.Model):
    first_name = models.CharField(max_length=64)
    middle_name = models.CharField(max_length=64, blank=True)
    surname = models.CharField(max_length=64)
    image = models.ImageField(upload_to='client_images', default='/media/person-placeholder.png')
    dob = models.DateField(default="1990-01-01")
    ni_regex = RegexValidator(regex=r'^(?!BG)(?!GB)(?!NK)(?!KN)(?!TN)(?!NT)(?!ZZ)(?:[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z])(?:\s*\d\s*){6}([A-D]|\s)$', message="Must be in the format: 'AA999999A', restrictions to characters apply'")
    ni_number = models.CharField(max_length=9, validators=[ni_regex], primary_key=True)
    email = models.EmailField(max_length=64)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Not a valid phone number. Up to 9 digits allowed.")
    home_phone = models.CharField(
        max_length=11, validators=[phone_regex], blank=True
    )
    mob_phone = models.CharField(
        max_length=11, validators=[phone_regex], blank=True
    )
    cash = models.DecimalField(max_digits=20, decimal_places=2)
    fa = models.ForeignKey(FA, null=True, blank=True)
    twitter_username = models.CharField(validators=[RegexValidator(
                                                    regex="^(\w){1,15}$",
                                                    message="Not a valid username,please remove @ and max of 15 cahracters"
                                                    )],
                                        blank=True, max_length= 15)
    facebook_username = models.CharField(blank=True, null=True, max_length=15)
    linkedin_username = models.CharField(blank=True, null=True, max_length=15)
    googleplus_username = models.CharField(blank=True, null=True, max_length=15)


    def __str__(self):
        return self.surname + " - " + self.ni_number

    def get_absolute_url(self):
        return reverse('edit_client', kwargs={'pk': self.pk})


class Event(models.Model):
    fa = models.ForeignKey(FA)
    client = models.ForeignKey(Client, blank=True, null=True)
    startDateTime = models.DateTimeField()
    endDateTime = models.DateTimeField()
    type = models.CharField(max_length=64, default="meeting")
    title = models.CharField(max_length=128)


    def __str__(self):
        return self.fa.first_name + " " + self.fa.surname + " - " + self.title + " - " + datetime.strftime(self.startDateTime, "%c")


class MeetingNotes(models.Model):
    event = models.OneToOneField(Event, null=True)
    note = models.TextField()

    def __str__(self):
        return self.note + " - " + self.event +\
            " " + datetime.strftime(self.event.startDateTime, "%c")


class Market(models.Model):
    name = models.CharField(primary_key=True, max_length=10)
    full_name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Stock(models.Model):
    symbol = models.CharField(primary_key=True, max_length=5)
    company = models.CharField(max_length=64)
    market = models.ForeignKey(Market)

    def __str__(self):
        return self.symbol


class Share(models.Model):
    owner = models.ForeignKey(Client)
    date = models.DateField(default="1990-01-01")
    amount = models.IntegerField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    stock = models.ForeignKey(Stock)
    buy = models.BooleanField(default=True)

    def __str__(self):
        return ""+str(self.buy)+ " - "+self.owner.surname +" - " + self.owner.ni_number + " - " + self.stock.symbol


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        widgets = {
            'cash': TextInput(
                attrs={'placeholder': '0.00', 'cols': '1', 'rows': '1'}),
            'dob': DateTimePicker(
                options={"format": "YYYY-MM-DD",
                         "viewMode": "years",
                         "pickSeconds": False})
        }

    def __str__(self):
        return self.first_name
