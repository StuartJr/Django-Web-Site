from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import Signal
from .utilities import send_activation_notification
from .utilities import get_timestamp_path
from django.db.models.signals import post_save
# from .utilities import send_new_comment_notification




user_registrated = Signal(providing_args = ['instance'])

def user_registrated_dispatcher(sender, **kwargs):
	send_activation_notification(kwargs['instance'])

user_registrated.connect(user_registrated_dispatcher)

class AdvUser(AbstractUser): #модель пользователя
	is_activated = models.BooleanField(default=True, db_index=True,
										verbose_name = 'Прошёл активацию?')
	send_messages = models.BooleanField(default=True, 
					verbose_name = 'Слать оповещения о новых комменариях?')

	def delete(self, *args, **kwargs):
		for bb in self.bb_set.all():
			bb.delete()
		super().delete(*args, **kwargs)

	class Meta(AbstractUser.Meta):
		pass

class Rubric(models.Model):#модель рубрик
	name = models.CharField(max_length=20, db_index=True, unique=True,
							verbose_name='Название')
	order = models.SmallIntegerField(default = 0, db_index=True,
							verbose_name = 'Порядок')
	super_rubric = models.ForeignKey('SuperRubric',
					on_delete = models.PROTECT, null = True, blank = True,
					verbose_name = 'Надрубрика') #хранит надрубрики

class SubRubricManager(models.Manager): #подрубрика
	def get_queryset(self):
		return super().get_queryset().filter(super_rubric__isnull = False)

class SubRubric(Rubric):
	objects = SubRubricManager()

	def __str__(self):#генерирует название подрубрики в виде строки
		return '%s - %s' % (self.super_rubric.name, self.name)

	class Meta:
		proxy = True
		ordering = ('super_rubric__order', 'super_rubric__name', 'order',
					'name')
		verbose_name = 'Подрубрика'
		verbose_name_plural = 'Подрубрика'

class SuperRubricManager(models.Manager):#надрубрики
	def get_queryset(self):
		return super().get_queryset().filter(super_rubric__isnull=True) #выбираем записи с пустым полем super_rubric

class SuperRubric(Rubric):
	objects = SuperRubricManager()

	def __str__(self):#генерирует название надрубрики в виде строки
		return self.name

	class Meta:
		proxy = True
		ordering = ('order', 'name')#сначала номер рубрики потом имя
		verbose_name = 'Надрубрика'
		verbose_name_plural = 'Надрубрика'



class Bb(models.Model): #основаня модель объявлений
	rubric = models.ForeignKey(SubRubric, on_delete=models.PROTECT,
								verbose_name = 'Рубрика')
	title = models.CharField(max_length=40, verbose_name = 'Товар')
	content = models.TextField(verbose_name = 'Описание')
	price = models.FloatField(default=0, verbose_name = 'Цена')
	contacts = models.TextField(verbose_name = 'Контакты')
	image = models.ImageField(blank=True, upload_to=get_timestamp_path,
							 verbose_name = 'Изображение')
	author = models.ForeignKey(AdvUser, on_delete = models.CASCADE,
							verbose_name = 'Автор объявлений')
	is_active = models.BooleanField(default=True, db_index=True,
									verbose_name = 'Выводить в списке?')
	created_at = models.DateTimeField(auto_now_add = True, db_index=True,
									verbose_name = 'Опубликовано')

	def delete(self, *args, **kwargs):#Удаление всех изображений связаных с объявлением
		for ai in self.additionalimage_set.all():
			ai.delete()
		super().delete(*args, **kwargs)

	class Meta:
		verbose_name_plural = 'Объявления'
		verbose_name = 'Объявление'
		ordering = ['created_at']

class Comment(models.Model):#коментраий
	bb = models.ForeignKey(Bb, on_delete=models.CASCADE,
							verbose_name = 'Объявление')
	author = models.CharField(max_length = 30,
								verbose_name = 'Автор')
	content = models.TextField(verbose_name = 'Содержание')
	is_active = models.BooleanField(default = True, db_index=True,
									verbose_name = 'Выводить на экран')
	created_at = models.DateTimeField(auto_now_add=True, db_index=True,
										verbose_name='Опубликован')
	class Meta:
		verbose_name_plural = 'Комментарии'
		verbose_name = 'Комментарии'
		ordering = ['created_at']#сортировка по увелечению даты и времени

class AdditionalImage(models.Model):#дополнительные иллюстрации
	bb = models.ForeignKey(Bb, on_delete=models.CASCADE,
							verbose_name = 'Объявление')
	image = models.ImageField(upload_to = get_timestamp_path,
							verbose_name = 'Изображение')

	class Meta:
		verbose_name_plural = 'Дополнительные иллюстрации'
		verbose_name = 'Дополнительная иллюстрация'


# def post_save_dispatcher(sender,  **kwargs):
# 	author = kwargs['instance'].bb.author
# 	if kwargs['created'] and author.send_messages:
# 		send_new_comment_notification(kwargs['instance'])

# post_save.connect(post_save_dispatcher, sender=Comment)		



