from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Task, Room, Notification, Comment
from django.core.mail import send_mail
from django.conf import settings
@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        room = instance.room
        sender = instance.sender
        participants = room.participants.exclude(id=sender.id)
        message = f"{sender.username} sent a message: {instance.content}"
        Notification.objects.bulk_create([
            Notification(room=room, sender=sender, recipient=participant, message=message)
            for participant in participants
        ])

# @receiver(post_save, sender=UploadedFile)
# def create_file_notification(sender, instance, created, **kwargs):
#     if created:
#         room = instance.room
#         sender = instance.uploaded_by
#         participants = room.participants.exclude(id=sender.id)
#         message = f"{sender.username} uploaded a file: {instance.file.name}"
#         Notification.objects.bulk_create([
#             Notification(room=room, sender=sender, recipient=participant, message=message)
#             for participant in participants
#         ])



@receiver(post_save, sender=Task)
def create_task_notification(sender, instance, created, **kwargs):
    if created:
        message = f"Task '{instance.title}' assigned to you in room '{instance.room.name}'"
        Notification.objects.create(room=instance.room, sender=instance.created_by, message=message)

        # Send email notification
        subject = 'New Task Assignment'
        message = f"Hello,\n\n{message}\n\nRegards,\n{settings.EMAIL_HOST_USER}"
        recipient_email = instance.assigned_to.email
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email])

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        message = f"New comment added to task '{instance.task.title}' in room '{instance.task.room.name}'"
        Notification.objects.create(room=instance.task.room, sender=instance.user, message=message)

        # Send email notification
        subject = 'New Comment on Task'
        message = f"Hello,\n\n{message}\n\nRegards,\n{settings.EMAIL_HOST_USER}"
        recipient_email = instance.task.assigned_to.email
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email])


# @receiver(post_save, sender=Branch)
# def create_branch_notification(sender, instance, created, **kwargs):
#     if created:
#         room = instance.room
#         sender = instance.created_by
#         participants = instance.participants.exclude(id=sender.id)
#         message = f"{instance.original_file.file.name} created by {sender.username}"
#         Notification.objects.bulk_create([
#             Notification(room=room, sender=sender, recipient=participant, message=message)
#             for participant in participants
#         ])