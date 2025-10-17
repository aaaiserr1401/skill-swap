from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            candidate = base
            i = 1
            while Skill.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                i += 1
                candidate = f"{base}-{i}"
            self.slug = candidate
        super().save(*args, **kwargs)


class User(AbstractUser):
    full_name = models.CharField(max_length=255, blank=True)
    university = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    points = models.IntegerField(default=0)
    skills_can_teach = models.ManyToManyField(Skill, related_name='teachers', blank=True)
    skills_to_learn = models.ManyToManyField(Skill, related_name='learners', blank=True)

    def __str__(self) -> str:
        if self.full_name:
            return self.full_name
        return super().__str__()


class ExchangeRequest(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_DECLINED = 'declined'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_DECLINED, 'Declined'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_exchanges')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_exchanges')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    sender_confirmed = models.BooleanField(default=False)
    receiver_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.sender} ↔ {self.receiver} · {self.skill} · {self.status}"

    def try_complete(self) -> bool:
        """If both sides confirmed, mark completed and grant points to both.
        Returns True if completion happened in this call.
        """
        if self.status == self.STATUS_COMPLETED:
            return False
        if self.sender_confirmed and self.receiver_confirmed and self.status in {self.STATUS_ACCEPTED, self.STATUS_PENDING}:
            self.status = self.STATUS_COMPLETED
            # Grant minimal points to both users
            self.sender.points = (self.sender.points or 0) + 1
            self.receiver.points = (self.receiver.points or 0) + 1
            self.sender.save(update_fields=['points'])
            self.receiver.save(update_fields=['points'])
            self.save(update_fields=['status'])
            return True
        return False

# Create your models here.
