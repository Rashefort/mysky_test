from django.urls import path
from . import views



urlpatterns = [
    path('', views.nomenclature, name='nomenclature'),
    path('signup/', views.signup, name='signup'),
    path('upload/', views.upload, name='upload'),
    path('images/', views.images, name='images'),
]
