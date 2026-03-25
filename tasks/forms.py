from django import forms

from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('title', 'description', 'status')
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'status': 'Статус',
        }

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 2:
            raise forms.ValidationError('Название должно быть не короче 2 символов.')
        return title
