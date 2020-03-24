from django.contrib import admin
import datetime
from .models import AdvUser
from .utilities import send_activation_notification
from .models import SuperRubric, SubRubric
from .forms import SubRubricForm


class SubRubricAdmin(admin.ModelAdmin):
	form = SubRubricForm

admin.site.register(SubRubric, SubRubricAdmin)

class SubRubricInline(admin.TabularInline):
	model = SubRubric

class SuperRubricAdmin(admin.ModelAdmin):
	exclude = ('super_rubric',)
	inlines = (SubRubricInline,)

admin.site.register(SuperRubric, SuperRubricAdmin)


def send_activation_notification(modeladmin, requset, queryset):
	for rec in queryset:
		if not rec.is_activated:
			send_activation_notification(rec)
	modeladmin.message_user(requset, 'Писмо с оповещениями отправлены')
send_activation_notification.short_description = 'Отправка писем с ' + \
'оповещениями об регестрации'

class NonactivatedFilter(admin.SimpleListFilter):
	title = 'Прошли активацию?'
	parameter_name = 'actstate'

	def lookups(self, requset, model_admin):
		return(
				('activated', 'Прошли'),
				('threedays', 'Не прошли более 3 дней'),
				('week', 'Не прошли более недели'),
			)

	def queryset(self, requset, queryset):
		val = self.value()
		if val == 'activated':
			return queryset.filter(is_active=True, is_activated=True)
		elif val == 'threedays':
			d = datetime.date.today() - datetime.timedelta(days=3)
			return queryset.filter(is_active=False, is_activated=False,
									date_joined__date__lt=d)
		elif val == 'week':
			d = datetime.date.today() - datetime.timedelta(weeks=1)
			return queryset.filter(is_active=False, is_activated=False,
									date_joined__date__lt=d)

class AdvUserAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'is_activated', 'date_joined')
	search_fields = ('username', 'email', 'first_name', 'last_name')
	list_filter = (NonactivatedFilter,)
	fields = (('username', 'email'), ('first_name', 'last_name'),
				('send_messages', 'is_active', 'is_activated'),
				('is_staff', 'is_superuser'),
				'groups', 'user_permissions',
				('last_login', 'date_joined'))
	readonly_fields = ('last_login', 'date_joined')
	actions = (send_activation_notification,)

admin.site.register(AdvUser, AdvUserAdmin)
# admin.site.register(AdvUser) #-вносим модель AdvUser на админ сайт
