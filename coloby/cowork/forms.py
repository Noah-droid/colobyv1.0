from django import forms
from .models import Task, Comment, Message, UploadedFile, Branch

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'assigned_to', 'completed']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file', 'content', 'description']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'tinymce'}),
            'file': forms.FileInput(attrs={'accept': 'image/*, video/*, audio/*, application/pdf'})
        }


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['original_file', 'content', 'description']
