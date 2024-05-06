from django.contrib.auth.models import AbstractUser
from collections.abc import Iterable
from django.db import models
from django.db.models.query import QuerySet

# Create your models here.
from django.utils import timezone
import uuid
from django.contrib.auth.models import User
# import shortuuid
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
import datetime
from tinymce.models import HTMLField


User = get_user_model()


import secrets

class APIKey(models.Model):
    key = models.CharField(max_length=270, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_key(cls):
        return secrets.token_urlsafe(32)

    @classmethod
    def create_for_user(cls, user):
        key = cls(key=cls.generate_key(), user=user)
        key.save()
        return key

class SoftDeletionManager(models.Manager):
    """
    A custom manager for models that support soft deletion. This manager filters out
    objects that have a non-null deleted_at field.
    """

    def __init__(self, *args, **kwargs):
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryself(self):
        return super(SoftDeletionManager, self).get_queryset().filter(deleted_at__isnull=True)

    def with_deleted(self):
        return super(SoftDeletionManager, self).get_queryset()


class BaseModel(models.Model):
    """
    An abstract base model that includes the deleted_at field and the SoftDeletionManager.
    This class will not be created as its own database table but will be inherited by other models
    via Meta class.
    """
    # deleted_at = models.DateTimeField(null=True, blank=True)
    objects = SoftDeletionManager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """
        Soft deletes the object by setting the deleted_at field to the current timestamp.
        """
        self.deleted_at = datetime.datetime.now()
        self.save()

    def restore(self):
        """
        Restores a soft-deleted object by setting the deleted_at field to null.
        """
        self.deleted_at = None
        self.save()


class Room(BaseModel):
    name = models.CharField(max_length=128)
    # unique_link = models.CharField(
    #     max_length=50, unique=True, default=uuid.uuid4().hex[:50])
    slug = models.SlugField(unique=True)
    users = models.ManyToManyField(CustomUser)
    is_private = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="created_rooms",
        null=True,
        blank=True,
        db_column='created_by'  # Set the db_column parameter
    )
    likes = models.ManyToManyField(
        CustomUser, related_name="liked_rooms", blank=True)
    description = models.CharField(max_length=300, blank=True, null=True)

    # def save(self, *args, **kwargs):
    #     if not self.unique_link or Room.objects.filter(unique_link=self.unique_link).exists():
    #         self.unique_link = uuid.uuid4().hex[:50]
    #         while Room.objects.filter(unique_link=self.unique_link).exists():
    #             self.unique_link = uuid.uuid4().hex[:50]
    #     super(Room, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class File(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255)
    path = models.FileField(upload_to='room_files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_staged = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Branch(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class StagedFile(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='staged_files')
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='staged_in')
    is_added = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.file.name} in {self.room.name} staging area"

class Message(BaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True, default=None)
    media = models.FileField(upload_to='media', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room.name} - {self.user.username}: {self.message}"

# A feature where users can create notes to pen ideas down


class UserNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    last_saved = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# Feature Request where room memebers can request a feature or something else


class FeatureRequest(models.Model):
    description = models.TextField()
    votes = models.PositiveIntegerField(default=0)
    implemented = models.BooleanField(default=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Task(BaseModel):
    PENDING = 'pending'
    DONE = 'done'
    UNDONE = 'undone'
    # Define choices for the status field
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (DONE, 'Done'),
        (UNDONE, 'Undone'),
        # Add more status choices as needed
    ]

    room = models.ForeignKey(Room, on_delete=models.RESTRICT)
    title = models.CharField(max_length=100)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    due_date = models.DateField()
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='tasks_created')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return self.title



class Comment(BaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.task.title}"



class Notification(BaseModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Activity: {self.message} carried out by {self.sender} in room: {self.room}"


