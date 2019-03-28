from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('load_data/', views.load_data, name='load_data'),
    path('API/get_main', views.get_main_graph, name='main')
]