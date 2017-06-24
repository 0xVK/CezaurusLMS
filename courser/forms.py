from django import forms
from courser.models import Course


class CourseForm(forms.ModelForm):

    name = forms.CharField(label='Назва', max_length=40, min_length=3,
                           widget=forms.TextInput(attrs={'class': 'form-control'}),)

    description = forms.CharField(label='Опис', max_length=80, required=False,
                                  widget=forms.Textarea(attrs={'class': 'form-control',
                                                               'rows': '4'}),)

    class Meta:
        model = Course
        fields = ['name', 'description']


class LectureForm(forms.Form):

    name = forms.CharField(label='Назва', max_length=100,
                           widget=forms.TextInput(attrs={'class': 'form-control'}),)

    description = forms.CharField(label="Опис", help_text="(необов'язково)", max_length=100, required=False,
                                  widget=forms.Textarea(attrs={'class': 'form-control',
                                                               'rows': '2'}),)

    text = forms.CharField(label='Текст', help_text='(підтримуються HTML теги, до 15 000 символів)', max_length=15000,
                           widget=forms.Textarea(attrs={'class': 'form-control',
                                                        'rows': '15'}), )

    is_available = forms.BooleanField(label='Матеріал доступний',
                                      help_text='(якщо галочка не стоїть, доступ до матеріалу буде закритий)',
                                      required=False, initial=True)


class IndependentWorkForm(forms.Form):

    name = forms.CharField(label='Назва', max_length=100,
                           widget=forms.TextInput(attrs={'class': 'form-control'}),)

    description = forms.CharField(label="Опис", help_text="(необов'язково)", max_length=100, required=False,
                                  widget=forms.Textarea(attrs={'class': 'form-control',
                                                               'rows': '2'}),)

    text = forms.CharField(label='Текст', help_text='(підтримуються HTML теги, до 15 000 символів)', max_length=15000,
                           widget=forms.Textarea(attrs={'class': 'form-control',
                                                        'rows': '15'}), )

    is_available = forms.BooleanField(label='Матеріал доступний',
                                      help_text='(якщо галочка не стоїть, доступ до матеріалу буде закритий)',
                                      required=False, initial=True)


class DictationForm(forms.Form):

    name = forms.CharField(label='Назва', max_length=100,
                           widget=forms.TextInput(attrs={'class': 'form-control'}),)

    description = forms.CharField(label="Опис", max_length=600, required=False,
                                  help_text="Цей текст буде показаний учням перед написанням диктанту. (необов'язково)",
                                  widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '5'}),)

    text = forms.CharField(label='Текст', max_length=15000,
                           help_text='Текст диктанту. Він буде використаний при перевірці результатів.',
                           widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '15'}), )

    audio = forms.FileField(label='Аудіофайл', widget=forms.FileInput(attrs={'accept': 'audio/*'}),
                            help_text='Аудіофайл, який буде відтворений при написанні. Доступні формати: mp3, wav, ogg',
                            required=False)

    is_available = forms.BooleanField(label='Матеріал доступний',
                                      help_text='(якщо галочка не стоїть, доступ до матеріалу буде закритий)',
                                      required=False, initial=True)

    show_results = forms.BooleanField(label='Показати результати',
                                      help_text='(якщо галочка не стоїть, учні не побачать результат перевірки)',
                                      required=False)


