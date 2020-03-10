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

from .models import AdvUser
from .forms import ChengeUserInfoForm

#Страница смены пароля
class BBPasswordChangeView(SuccessMessageMixin, LoginRequiredMixin,
												PasswordChangeView):
	template_name = 'bboard/password_change.html'
	success_url = reverse_lazy('bboard:profile')
	success_message = 'Пароль пользователя изменён'

#Страница с изменение личных данных пользователя
class ChengeUserInfoView(SuccessMessageMixin, LoginRequiredMixin,
											UpdateView):
	model = AdvUser # используемая модель
	template_name = 'bboard/change_user_info.html' # используемый шаблон
	form_class = ChengeUserInfoForm # используемая форма
	success_url = reverse_lazy('bboard:profile')
	success_message = 'Личные данные пользователя изменены' 

	def dispatch(self, request, *args, **kwargs):
		self.user_id = request.user.pk #-извлекаем и сохраняем ключ пользователя
		return super().dispatch(request, *args, **kwargs)

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