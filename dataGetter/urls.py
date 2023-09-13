from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("ajax-add/", views.test_ajax),

]