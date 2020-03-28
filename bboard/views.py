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
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect

from .models import AdvUser
from .forms import ChengeUserInfoForm
from .forms import RegisterUserForm
from .utilities import signer
from .models import SubRubric, Bb
from .forms import SearchForm
from .forms import BbForm, AIFormSet

@login_required
def profile_bb_change(request, pk):
	bb = get_object_or_404(Bb, pk=pk)
	if request.method == 'POST':
		form = BbForm(request.POST, request.FILES, instance=bb)
		if form.is_valid():
			bb = form.save()
			formset = AIFormSet(request.POST, request.FILES, instance=bb)
			if formset.is_valid():
				formset.save()
				messages.add_message(request, messages.SUCCESS,
									'Объявление исправлено')
				return redirect('bboard:profile')
	else:
		form = BbForm(instance=bb)
		formset = AIFormSet(instance=bb)
		context = {'form': form, 'formset':formset}
		return render(request, 'bboard/profile_bb_change.html', context)

@login_required
def profile_bb_delete(request, pk):
	bb = get_object_or_404(Bb, pk=pk)
	if request.method == 'POST':
		bb.delete()
		messages.add_message(request, messages.SUCCESS, 
							'Объявление удалено')
		return redirect('bboard:profile')
	else:
		context = {'bb':bb }
		return render(request, 'bboard/profile_bb_delete.html', context)

@login_required
def profile_bb_add(request):
	if request.method == 'POST':
		form = BbForm(request.POST, request.FILES)
		if form.is_valid():
			bb = form.save()
			formset = AIFormSet(request.POST, request.FILES, instance = bb)
			if formset.is_valid():
				formset.save()
				messages.add_message(request, messages.SUCCESS,
									'Объявление добавлено')
				return redirect('bboard:profile')
	else:
		form = BbForm(initial = {'author':request.user.pk})
		formset = AIFormSet()
	context = {'form':form, 'formset': formset}
	return render(request, 'bboard/profile_bb_add.html', context)

#страница добавленных пользователем объявлений
@login_required
def profile_bb_detail(request, pk):
    bb = get_object_or_404(Bb, pk=pk)
    ais = bb.additionalimage_set.all()
    comments = Comment.objects.filter(bb=pk, is_active=True)
    context = {'bb': bb, 'ais': ais, 'comments': comments}
    return render(request, 'bboard/profile_bb_detail.html', context)

#страница деталей объявления
def detail(request, rubric_pk, pk):
	bb = get_object_or_404(Bb, pk=pk)#выводим модель Bb или ошибку 404
	ais = bb.additionalimage_set.all()#берём все дополнительные изображения
	context = {'bb':bb, 'ais':ais }
	return render(request, 'bboard/detail.html', context)

#страница списка обявлений и поиска
def by_rubric(request, pk):
	rubric = get_object_or_404(SubRubric, pk=pk)#выводим подрубрику выбранную пользователем
	bbs = Bb.objects.filter(is_active = True, rubric=pk) #выводим те объявления которые активны
	if 'keyword' in request.GET: #если в поле поиска что-то введено то
		keyword = request.GET['keyword']#получаем это слово
		q = Q(title__icontains=keyword) | Q(content__icontains=keyword) #проверяет в СУБД есть ключевое слово в название или описании(без учёта регистра)
		bbs = bbs.filter(q)#применяем фильтрацию к объявлениям
	else:
		keyword = ''
	form = SearchForm(initial={'keyword': keyword})#кючевое слово выводится вместе с фомрой
	paginator = Paginator(bbs, 2)
	if 'page' in request.GET:
		page_num = request.GET['page']
	else:
		page_num = 1 
	page = paginator.get_page(page_num)
	context = {'rubric':rubric, 'page':page, 'bbs':page.object_list,
				'form':form}
	return render(request, 'bboard/by_rubric.html', context)


#страница удаления пользователя
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
	bbs = Bb.objects.filter(author=request.user.pk)
	context = {'bbs': bbs}
	return render(request, 'bboard/profile.html', context)

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
	bbs = Bb.objects.filter(is_active=True)[:10]
	context = {'bbs':bbs }
	return render(request, 'bboard/index.html', context)