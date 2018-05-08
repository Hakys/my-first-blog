from django.conf.urls import include, url
from . import views

urlpatterns = [
	url(r'^$', views.product_list, name='product_list'),
	url(r'^reload/$', views.product_reload, name='product_reload'),
]
