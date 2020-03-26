from django.urls import path

from .views import index
from .views import other_page
from .views import BBLoginView
from .views import BBLogoutView
from .views import profile
from .views import ChengeUserInfoView
from .views import BBPasswordChangeView
from .views import RegisterUserView, RegisterDoneView
from .views import user_activate
from .views import DeleteUserView
from .views import by_rubric
from .views import detail 

app_name='bboard' #Название приложения из пространства имён для сопоставления URL-адресов.
urlpatterns = [
	path('accounts/register/activate/<str:sign>', user_activate,
	 	name = 'register_activate'),
	path('accounts/register/done/', RegisterDoneView.as_view(), 
		name = 'register_done'),
	path('accounts/register/', RegisterUserView.as_view(), 
		name = 'register'),
	path('accounts/password/change/', BBPasswordChangeView.as_view(), 
		name = 'password_change'),
	path('accounts/profile/delete/', DeleteUserView.as_view(),
		name = 'profile_delete'),
	path('accounts/profile/change/', ChengeUserInfoView.as_view(), 
		name = 'profile_change'),
	path('accounts/profile/', profile, name = 'profile'),
	path('accounts/logout/', BBLogoutView.as_view(), name = 'logout'),
	path('<int:rubric_pk>/<int:pk>/', detail, name = 'detail'),
	path('<int:pk>/', by_rubric, name='by_rubric'),
	path('accounts/login/', BBLoginView.as_view(), name = 'login'),
	path('<str:page>/', other_page, name = 'other'),
	path('', index, name='index'),
]