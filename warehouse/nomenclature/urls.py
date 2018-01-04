from django.urls import path
from . import views


urlpatterns = [
    path('', views.nomenclature, name='nomenclature'),
    path('signup/', views.signup, name='signup'),
]
