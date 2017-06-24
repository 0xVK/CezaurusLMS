from django import forms
from django.utils.translation import ugettext as _
import core.validators as val


class SignUpForm(forms.Form):

    username = forms.CharField(label='Логін', max_length=25, validators=[val.unique_username_ignore_case_validator,
                                                                         val.forbidden_username_validator,
                                                                         val.correct_format_validator, ])
    first_name = forms.CharField(label="Ім'я", max_length=12)
    last_name = forms.CharField(label='Прізвище', max_length=15)
    sex = forms.ChoiceField(choices=(('M', 'Чоловік'), ('W', 'Жінка')))
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Пароль', max_length=35, min_length=5)
    password2 = forms.CharField(label='Пароль ще раз', max_length=35, min_length=5)
    birthday = forms.DateField(label='Дата народження (dd.mm.yyyy)', input_formats=['%d.%m.%Y'])
    location = forms.CharField(label='Місто', max_length=30)
    school = forms.CharField(label='Навчальний заклад', max_length=40, required=False)
    form = forms.CharField(label='Клас або група', max_length=10, required=False)

    def clean(self):
        super(SignUpForm, self).clean()
        password = self.cleaned_data.get('password1')
        confirm_password = self.cleaned_data.get('password2')
        if password != confirm_password:
            self._errors['password2'] = self.error_class(
                [_('Паролі не співпадають')])
        return self.cleaned_data


