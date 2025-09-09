from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
	path('', views.HomeView.as_view(), name='home'),
	path('dashboard/', views.SuperuserDashboardView.as_view(), name='superuser_dashboard'),
	path('profile/', views.profile, name='profile'),
	path('user-management/', views.user_management, name='user_management'),
	path('survey-results/', views.survey_results, name='survey_results'),
	path('article/create/', views.ArticleCreateView.as_view(), name='article_create'),
	path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
	path('article/<slug:slug>/delete/', views.ArticleDeleteView.as_view(), name='article_delete'),
	path('surveys/', views.SurveyListView.as_view(), name='survey_list'),
	path('survey/create/', views.SurveyCreateView.as_view(), name='survey_create'),
	path('survey/<int:pk>/edit/', views.survey_edit, name='survey_edit'),
	path('survey/<int:pk>/delete/', views.SurveyDeleteView.as_view(), name='survey_delete'),
	path('survey/<int:pk>/submitted/', views.SurveySubmittedView.as_view(), name='survey_submitted'),
	path('surveys/<int:pk>/', views.SurveyDetailView.as_view(), name='survey_detail'),
]