from django.conf.urls import include, url
from . import views

urlpatterns = [
	url(r'^$', views.product_grid, name='product_grid'), 

    url(r'^templateshop/$', views.templateshop, name="templateshop"),
    url(r'^cron/$', views.externo_cron, name='externo_cron'),
    url(r'^test/$', views.product_test, name='product_test'),     
    url(r'^reload/$', views.product_reload, name='product_reload'),
    
    url(r'^product/$', views.product_list, name='product_list'),
    url(r'^product/(?P<pk>[0-9]+)/$', views.product_detail, name='product_detail'),    
    url(r'^search/$', views.product_search, name='product_search'),

    url(r'^ext/$', views.externo_list, name='externo_list'),
    url(r'^ext/dreamlove/$', views.externo_dreamlove, name='externo_dreamlove'),
    url(r'^ext/(?P<pk>[0-9]+)/$', views.externo_detail, name='externo_detail'),
    url(r'^ext/(?P<pk>[0-9]+)/edit/$', views.externo_edit, name='externo_edit'),
    url(r'^ext/(?P<pk>[0-9]+)/importar/$', views.externo_importar, name='externo_importar'),
    url(r'^ext/(?P<pk>[0-9]+)/procesar_productos/$', views.externo_procesar_productos, name='externo_procesar_productos'),
    url(r'^ext/(?P<pk>[0-9]+)/procesar_imagenes/$', views.externo_procesar_imagenes, name='externo_procesar_imagenes'),
    #url(r'^ext/(?P<pk>[0-9]+)/procesar_categorias/$', views.externo_procesar_categorias, name='externo_procesar_categorias'), 
    url(r'^ext/(?P<pk>[0-9]+)/procesar_fabricantes/$', views.externo_procesar_fabricantes, name='externo_procesar_fabricantes'),   
    
    url(r'^fabricante/$', views.fabricante_list, name='fabricante_list'),
    url(r'^fabricante/(?P<hierarchy>.+)/$', views.fabricante_show, name='fabricante_show'),
    
    ]
