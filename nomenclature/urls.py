from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.artefact_list, name='artefact_list'),
]
