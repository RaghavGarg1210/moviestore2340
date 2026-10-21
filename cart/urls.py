from django.urls import path
from . import views
urlpatterns = [
    path('<int:id>/add/', views.add, name='cart.add'),
    path('', views.index, name='cart.index'),
    path('clear/', views.clear, name='cart.clear'),
    path('purchase/', views.purchase, name='cart.purchase'),
    path('top-buyer/', views.top_buyer, name='cart.top_buyer'),
    path('movie-stats/', views.movie_stats, name='cart.movie_stats'),
    path('top-buyers/', views.top_buyers, name='cart.top_buyers'),

]
