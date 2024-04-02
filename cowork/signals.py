from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Task, Room, Notification 

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
        room = instance.room
        sender = instance.created_by
        participants = instance.participants.exclude(id=sender.id)
        message = f"{sender.username} assigned {instance.participants} to {instance.title}"
        Notification.objects.bulk_create([
            Notification(room=room, sender=sender, recipient=participant, message=message)
            for participant in participants
        ])

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