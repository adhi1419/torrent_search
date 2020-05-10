from django.urls import path

from . import views

app_name = 'search'
urlpatterns = [
	path('', views.index, name='index'),
	path('results/', views.results, name='results'),
	path('refresh/', views.refresh, name='refresh'),
	path('fetch_results/', views.fetch_results, name='fetch_results'),
]