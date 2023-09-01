from django import forms
from .models import CommentModel


class SearchProductForm(forms.Form):
    search = forms.CharField(max_length=50)


class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ('text',)


class CommentReplyForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ('text',)
