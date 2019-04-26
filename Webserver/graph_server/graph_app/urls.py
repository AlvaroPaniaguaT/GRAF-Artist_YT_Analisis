from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('load_data/', views.load_data, name='load_data'),
    path('ev_centrality/', views.eigenvector_view, name='ev_centrality'),
    path('pagerank/', views.page_rank_view, name='pagerank'),
    path('modularity/', views.modularity_view, name='modularity'),
    path('API/get_main', views.get_main_graph, name='main_APIREST'),
    path('API/eigenvector', views.calculate_eigenvector, name='eigenvector_APIREST'),
    path('API/pagerank', views.calculate_pagerank, name='pagerank_APIREST'),
    path('API/get_modularity', views.calculate_modularity, name='modularity_APIREST'),
]