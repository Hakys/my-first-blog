from django.conf.urls import include, url
from . import views

urlpatterns = [
	url(r'^$', views.product_list, name='product_list'),    
    url(r'^product/$', views.product_grid, name='product_grid'),
    url(r'^product/(?P<pk>[0-9]+)/$', views.product_detail, name='product_detail'),
    url(r'^reload/$', views.product_reload, name='product_reload'),
    url(r'^test/$', views.product_test, name='product_test'), 

    url(r'^ext/$', views.externo_list, name='externo_list'),
    url(r'^ext/dreamlove/$', views.externo_dreamlove, name='externo_dreamlove'),
    url(r'^ext/(?P<pk>[0-9]+)/$', views.externo_detail, name='externo_detail'),
    url(r'^ext/(?P<pk>[0-9]+)/edit/$', views.externo_edit, name='externo_edit'),
    url(r'^ext/(?P<pk>[0-9]+)/importar/$', views.externo_importar, name='externo_importar'),
    url(r'^ext/(?P<pk>[0-9]+)/procesar/$', views.externo_procesar, name='externo_procesar'),
    ]
