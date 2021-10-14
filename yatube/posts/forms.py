from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text', 'image')


class CommentForm(forms.ModelForm):
    def clean_text(self):
        if self.cleaned_data['text'] is None:
            raise forms.ValidationError(
                'Пожалуйста, заполните это поле',
                params={'value': self.cleaned_data['text']},
            )
        return self.cleaned_data['text']

    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': 'Прокомментируйте этот пост'
        }
        help_texts = {
            'text': 'Здесь нужно ввести текст комментрия'
        }
