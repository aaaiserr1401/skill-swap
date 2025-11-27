from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='skill_photos/', null=True, blank=True)
    experience_years = models.PositiveIntegerField(null=True, blank=True)

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
    points = models.IntegerField(default=20)
    points_hold = models.IntegerField(default=0)
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
    message = models.TextField(blank=True)
    price = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    sender_confirmed = models.BooleanField(default=False)
    receiver_confirmed = models.BooleanField(default=False)
    sender_confirmed_at = models.DateTimeField(null=True, blank=True)
    receiver_confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.sender} ↔ {self.receiver} · {self.skill} · {self.status}"

    def hold_from_sender(self) -> bool:
        """Atomically hold price points from sender for this request.

        Returns True if hold succeeded, False if sender has insufficient points.
        """
        from django.db import transaction
        from django.db.models import F

        if self.price <= 0:
            return True

        if not self.sender_id and self.sender:
            self.sender_id = self.sender.pk

        with transaction.atomic():
            sender_locked = User.objects.select_for_update().get(pk=self.sender_id)
            if sender_locked.points < self.price:
                return False
            sender_locked.points = F('points') - self.price
            sender_locked.points_hold = F('points_hold') + self.price
            sender_locked.save(update_fields=['points', 'points_hold'])
            if self.pk is None:
                self.status = self.STATUS_PENDING
                self.save()
        return True

    def refund_to_sender(self) -> None:
        """Atomically refund held points to sender and mark request declined."""
        from django.db import transaction
        from django.db.models import F

        if self.price <= 0:
            self.status = self.STATUS_DECLINED
            self.save(update_fields=['status'])
            return

        with transaction.atomic():
            sender_locked = User.objects.select_for_update().get(pk=self.sender_id)
            sender_locked.points_hold = F('points_hold') - self.price
            sender_locked.points = F('points') + self.price
            sender_locked.save(update_fields=['points_hold', 'points'])
            self.status = self.STATUS_DECLINED
            self.save(update_fields=['status'])

    def try_complete(self) -> bool:
        """If both sides confirmed, mark completed and grant points to both.
        Returns True if completion happened in this call.
        """
        if self.status == self.STATUS_COMPLETED:
            return False
        if self.sender_confirmed and self.receiver_confirmed and self.status in {self.STATUS_ACCEPTED, self.STATUS_PENDING}:
            # Finalize transaction: move hold from sender to receiver and give bonus +1 to both
            from django.db import transaction
            from django.db.models import F
            with transaction.atomic():
                # reload users with select_for_update to avoid races
                sender_locked = User.objects.select_for_update().get(pk=self.sender_id)
                receiver_locked = User.objects.select_for_update().get(pk=self.receiver_id)
                # Ensure hold covers price
                hold_to_release = min(max(sender_locked.points_hold, 0), max(self.price, 0))
                # Deduct hold and points from sender; credit receiver
                sender_locked.points_hold = F('points_hold') - hold_to_release
                sender_locked.points = F('points') - hold_to_release + 10
                receiver_locked.points = F('points') + hold_to_release + 10
                sender_locked.save(update_fields=['points_hold', 'points'])
                receiver_locked.save(update_fields=['points'])
                self.status = self.STATUS_COMPLETED
                self.save(update_fields=['status'])
            return True
        return False

# Create your models here.
