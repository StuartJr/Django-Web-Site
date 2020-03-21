from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .models import AdvUser
from .models import user_registrated

class RegisterUserForm(forms.ModelForm):
	email = forms.EmailField(required=True,
							label='Адрес электронной почты')
	password1 = forms.CharField(label = 'Пароль', 
		widget=forms.PasswordInput,
		help_text = password_validation.password_validators_help_text_html())
	password2 = forms.CharField(label = 'Пароль (повторно)',
		widget = forms.PasswordInput,
		help_text = 'Введите пароль ещё раз для проверки')

	def clean_password(self): #- проверяем пароль на корректность
		password1=self.cleaned_data['password1']
		if password1:
			password_validation.validate_password(password1)
		return password1

	def clean(self): #- проверяем совпадают ли пароли
		super().clean()
		password1=self.cleaned_data['password1']#получаем данные через объект cleaned_data
		password2=self.cleaned_data['password2']#получаем данные через объект cleaned_data
		if password1 and password2 and password1 != password2:
			errors = {'password2': ValidationError(
				'Введенные пароли не совпадают', code = 'password_mismatch')}
			raise ValidationError(errors)

	def save(self, commit=True): #-сохраняем пользователя
		user = super().save(commit=False)
		user.set_password(self.cleaned_data['password1']) # устанавливаем пороль пользователя
		user.is_active = False #при создание нового пользователя он не активен
		user.is_activated = False #при создание нового пользователя он не прошёл активацию
		if commit:
			user.save()
		user_registrated.send(RegisterUserForm, instance=user)#если такой аргумент указан(instance), то save() обновит переданную модель
		return user

	class Meta:
		model = AdvUser
		fields = ('username', 'email','password1', 'password2',
		 		'first_name', 'last_name', 'send_messages')

class ChengeUserInfoForm(forms.ModelForm):
	email = forms.EmailField(required=True,#обязательно к заполнению
							label='Адрес электронной почты')

	class Meta:
		model = AdvUser
		fields = ('username', 'email', 'first_name', 'last_name',
					'send_messages')