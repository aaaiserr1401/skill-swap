from django.db import models
from django.contrib.auth.models import AbstractUser


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class User(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True)
    university = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    skills_can_teach = models.ManyToManyField(Skill, related_name='teachers', blank=True)
    skills_to_learn = models.ManyToManyField(Skill, related_name='learners', blank=True)

    def __str__(self) -> str:
        if self.full_name:
            return self.full_name
        return super().__str__()

# Create your models here.
