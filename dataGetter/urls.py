from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("data-refresh/", views.data_refresher),
  ]