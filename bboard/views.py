from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.template.loader import get_template 
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import PasswordChangeView
from django.views.generic.base import TemplateView
from django.core.signing import BadSignature
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.contrib.auth import logout
from django.contrib import messages

from .models import AdvUser
from .forms import ChengeUserInfoForm
from .forms import RegisterUserForm
from .utilities import signer

class DeleteUserView(LoginRequiredMixin, DeleteView):
	model = AdvUser
	template_name = 'bboard/delete_user.html'
	success_url = reverse_lazy('bboard:index')

	def dispatch(self, request, *args, **kwargs):
		self.user_id = request.user.pk #-извлекаем и сохраняем ключ пользователя
		return super().dispatch(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		logout(request)
		messages.add_message(request, messages.SUCCESS,
										'Пользователь удалён')
		return super().post(request, *args, **kwargs)

	def get_object(self, queryset=None): #-извлекаем исправляемую запись
		if not queryset:
			queryset = self.get_queryset()
		return get_object_or_404(queryset, pk=self.user_id)

#Страница активации пользователя
def user_activate(request, sign):
	try:
		username = signer.unsign(sign)#цифровая подпись
	except BadSignature:
		return render(request, 'bboard/bad_signature.html') #Активация пользователя с таким именем прошла неудачно
	user = get_object_or_404(AdvUser, username=username)
	if user.is_activated: #Активация пользователя с таким именем был активирован ранее
		template = 'bboard/user_is_activated.html'
	else: #Пользователь с таким именем успешно активирован
		template = 'bboard/activation_done.html'
		user.is_active = True #пользователь активен
		user.is_activated = True #пользователь активирован
		user.save()
	return render(request, template)

#Страница об успешной регистрации ользователя
class RegisterDoneView(TemplateView):
	template_name = 'bboard/register_done'

#Страница регистрации пользователя
class RegisterUserView(CreateView):
	model = AdvUser
	template_name = 'bboard/register_user.html'
	form_class = RegisterUserForm
	success_url = reverse_lazy('bboard:register_done')

#Страница смены пароля
class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin,
												PasswordChangeView):
	template_name = 'bboard/password_change.html'
	success_url = reverse_lazy('bboard:profile')
	success_message = 'Пароль пользователя изменён' #всплывающее сообщение

#Страница с изменение личных данных пользователя
class ChengeUserInfoView(SuccessMessageMixin, LoginRequiredMixin,
											UpdateView):
	model = AdvUser # используемая модель
	template_name = 'bboard/change_user_info.html' # используемый шаблон
	form_class = ChengeUserInfoForm # используемая форма
	success_url = reverse_lazy('bboard:profile') #страница, которая используется в случае успешного проведения операции
	#reverse_lazt - Эта функция может быть полезна в случае, если вам нужно вернуть URL-адрес прежде, чем ваши настройки URLConf будут загружены.
	success_message = 'Личные данные пользователя изменены' #всплывающее сообщение

	def dispatch(self, request, *args, **kwargs):
		self.user_id = request.user.pk #-извлекаем и сохраняем ключ пользователя
		return super().dispatch(request, *args, **kwargs) #super()-возможность использования в классе потомке, методов класса-родителя.

	def get_object(self, queryset=None): #-извлекаем исправляемую запись
		if not queryset:
			queryset = self.get_queryset()
		return get_object_or_404(queryset, pk=self.user_id)

#Страница профиля
@login_required
def profile(request):
	return render(request, 'bboard/profile.html')

#Страница выхода
class BBLogoutView(LogoutView):
	template_name = 'bboard/logout.html'

#Страница авторизации
class BBLoginView(LoginView):
	template_name = 'bboard/login.html'

# Дополнительные страницы
def other_page(request, page):
	try:
		template = get_template('bboard/' + page + '.html')
	except TemplateDoesNotExist: 
		raise Http404
		#не удалось загрузить шаблон
	return HttpResponse(template.render(request=request))

# Главная страница
def index(request):
	return render(request, 'bboard/index.html')