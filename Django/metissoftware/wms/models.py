from django.db import models
from django.forms import ModelForm, TextInput
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)


# Create your models here.

class User(models.Model):
    first_name = models.CharField(max_length=64, default="**DEFAULT**")
    surname = models.CharField(max_length=64, default="**DEFAULT**")
    dob = models.DateField(default="1990-01-01")
    ni_regex = RegexValidator(regex=r'^(?!BG)(?!GB)(?!NK)(?!KN)(?!TN)(?!NT)(?!ZZ)(?:[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z])(?:\s*\d\s*){6}([A-D]|\s)$', message="Must be in the format: 'AA999999A', restrictions to characters apply'")
    ni_number = models.CharField(max_length=9, validators=[ni_regex], primary_key=True)
    email = models.EmailField(max_length=64, default="**DEFAULT**")

    class Meta:
        abstract = True


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
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, surname,
                         dob, ni_number, password, **extra_fields):

        user = self.create_user(email, first_name, surname, dob,
                                ni_number, password, **extra_fields)

        user.is_superuser = True
        user.save(using=self._db)
        return user


class FA(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=64, unique=True)
    first_name = models.CharField(max_length=64, default="**DEFAULT**")
    surname = models.CharField(max_length=64, default="**DEFAULT**")
    dob = models.DateField(default="1990-01-01")
    ni_regex = RegexValidator(regex=r'^(?!BG)(?!GB)(?!NK)(?!KN)(?!TN)(?!NT)(?!ZZ)(?:[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z])(?:\s*\d\s*){6}([A-D]|\s)$', message="Must be in the format: 'AA999999A', restrictions to characters apply'")
    ni_number = models.CharField(
        max_length=9, validators=[ni_regex], primary_key=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'surname', 'dob', 'ni_number']

    objects = FAUserManager()


class Client(User):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Not a valid phone number. Up to 9 digits allowed.")
    middle_name = models.CharField(max_length=64, null=True)
    home_phone = models.CharField(
        max_length=11, validators=[phone_regex], blank=True
    )
    mob_phone = models.CharField(
        max_length=11, validators=[phone_regex], blank=True
    )
    cash = models.DecimalField(max_digits=20, decimal_places=2)
    fa = models.ForeignKey(FA)

    def __str__(self):
        return self.surname + " - " + self.ni_number


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
    buy_date = models.DateField(default="1990-01-01")
    amount = models.IntegerField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    stock = models.ForeignKey(Stock)

    def __str__(self):
        return self.owner.surname + " \
               " + self.owner.ni_number + " - " + self.stock.symbol


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'middle_name', 'surname', 'email',
                  'mob_phone', 'home_phone', 'dob', 'ni_number', 'fa', 'cash']
        widgets = {
            'cash': TextInput(
                attrs={'placeholder': '0.00', 'cols': '1', 'rows': '1'}
            ),
        }

    def __str__(self):
        return self.first_name
