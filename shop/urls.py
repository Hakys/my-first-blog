from django.conf.urls import include, url
from . import views

urlpatterns = [
	url(r'^$', views.product_list, name='product_list'),    
    url(r'^product/(?P<id>[0-9]+)/$', views.product_detail, name='product_detail'),
    url(r'^reload/$', views.product_reload, name='product_reload'),
    url(r'^test/$', views.product_test, name='product_test'), 

    url(r'^ext/$', views.externo_list, name='externo_list'),
    url(r'^ext/dreamlove/$', views.externo_dreamlove, name='externo_dreamlove'),
    url(r'^ext/(?P<pk>[0-9]+)/$', views.externo_detail, name='externo_detail'),
    url(r'^ext/(?P<pk>[0-9]+)/edit/$', views.externo_edit, name='externo_edit'),
    url(r'^ext/(?P<pk>[0-9]+)/importar/$', views.externo_importar, name='externo_importar'),

    ]
