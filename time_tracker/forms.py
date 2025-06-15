from django import forms
from .models import Task, TaskCategory, TaskExecutionLog


class TaskForm(forms.ModelForm):
    """タスクフォーム"""
    
    class Meta:
        model = Task
        fields = ['title', 'category', 'estimated_minutes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'タスク名を入力してください'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estimated_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '見積時間（分）',
                'min': '1'
            })
        }
        labels = {
            'title': 'タスク名',
            'category': 'カテゴリ',
            'estimated_minutes': '見積時間（分）'
        }


class TaskCategoryForm(forms.ModelForm):
    """タスクカテゴリフォーム"""
    
    class Meta:
        model = TaskCategory
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'カテゴリ名を入力してください'
            }),
            'color': forms.TextInput(attrs={
                'type': 'color',
                'class': 'form-control form-control-color',
                'title': 'カテゴリの色を選択してください'
            })
        }
        labels = {
            'name': 'カテゴリ名',
            'color': '色'
        }


class TaskExecutionLogForm(forms.ModelForm):
    """タスク実行ログフォーム"""
    
    class Meta:
        model = TaskExecutionLog
        fields = ['start_time', 'end_time', 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'メモがあれば入力してください'
            })
        }
        labels = {
            'start_time': '開始時刻',
            'end_time': '終了時刻',
            'notes': 'メモ'
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError('終了時刻は開始時刻より後である必要があります。')
        
        return cleaned_data