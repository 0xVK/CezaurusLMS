from django import forms
from communities.models import *


class DiscussionForm(forms.ModelForm):

    title = forms.CharField(label='Назва', max_length=60,
                            widget=forms.TextInput(attrs={'class': 'form-control'}),)

    text = forms.CharField(label='Текст', max_length=2500,
                           widget=forms.Textarea(attrs={'class': 'form-control',
                                                        'rows': '8'}),)

    class Meta:
        model = Discussion
        fields = ['title', 'text']


class CommunityForm(forms.ModelForm):

    name = forms.CharField(label='Назва', max_length=30, min_length=3,
                           widget=forms.TextInput(attrs={'class': 'form-control'}),)
    description = forms.CharField(label='Опис', max_length=50, required=False,
                                  widget=forms.Textarea(attrs={'class': 'form-control',
                                                               'rows': '4'}),)

    class Meta:
        model = Community
        fields = ['name', 'description']
