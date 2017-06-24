from django import forms
from django.contrib.auth.models import User


class ProfileForm(forms.ModelForm):

    first_name = forms.CharField(label="Ім'я", max_length=12,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}),)

    last_name = forms.CharField(label='Прізвище', max_length=15,
                                widget=forms.TextInput(attrs={'class': 'form-control'}),)

    status = forms.CharField(label='Статус', max_length=140, required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control'}),)

    email = forms.EmailField(label='Email', max_length=50,
                             widget=forms.TextInput(attrs={'class': 'form-control'}),)

    birthday = forms.DateField(label='Дата народження (dd.mm.yyyy)', input_formats=['%d-%m-%Y',
                                                                                    '%d.%m.%Y', ], required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control'}),)

    location = forms.CharField(label='Місто', max_length=30, required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control'}),)

    school = forms.CharField(label='Навчальний заклад', max_length=40, required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control'}),)

    form = forms.CharField(label='Клас або група', max_length=10, required=False,
                           widget=forms.TextInput(attrs={'class': 'form-control'}),)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'status', 'email', 'birthday', 'location', 'school', 'form',]


class ChangePasswordForm(forms.ModelForm):
    id = forms.CharField(widget=forms.HiddenInput())

    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Старий пароль", required=True)

    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Новий пароль", required=True)
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Новий пароль ще раз", required=True)

    class Meta:
        model = User
        fields = ['id', 'old_password', 'new_password', 'confirm_password']

    def clean(self):
        super(ChangePasswordForm, self).clean()
        old_password = self.cleaned_data.get('old_password')
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        id = self.cleaned_data.get('id')
        user = User.objects.get(pk=id)

        if not user.check_password(old_password):
            self._errors['old_password'] = self.error_class([
                'Старий пароль не правильний.'])
        if new_password and new_password != confirm_password:
            self._errors['new_password'] = self.error_class([
                'Паролі не співпадають!'])
            self._errors['confirm_password'] = self.error_class([
                ''])

        return self.cleaned_data
