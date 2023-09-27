from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("index/", views.index),
    path("data-refresh/", views.data_refresher),
    path('fund_list_add/', views.add_fund),
    path('fund_manage/', views.fund_list),
    path('fund_list_del/<str:fund_code>/', views.del_fund),
  ]

from django.conf.urls import static
from fundAssist import settings
urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
