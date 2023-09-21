from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("data-refresh/", views.data_refresher),
    path('fund_list_add/', views.add_fund),
    path('fund_manage/', views.fund_list),
    path('fund_list_del/<str:fund_code>/', views.del_fund),
  ]
