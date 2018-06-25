from django.conf.urls import include, url
from . import views
from django.urls import path
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^$', views.index, name='index'), 
	url(r'^fab/$', views.fabricante_home, name='fabricante_home'),
    url(r'^fab/(?P<slug>.+)/$', views.fabricante_detail, name='fabricante_detail'),

    url(r'^templateshop/$', views.templateshop, name="templateshop"),
    
    url(r'^ext/$', views.externo_home, name='externo_home'),
    url(r'^ext/init_loadfile/$', views.init_loadfile, name='init_loadfile'),

    url(r'^cron/$', views.externo_cron, name='externo_cron'),
    url(r'^test/$', views.test, name='test'),     
    url(r'^reload/$', views.product_reload, name='product_reload'),
    
    url(r'^product/$', views.product_home, name='product_home'), 
    url(r'^product_list/$', views.product_list, name='product_list'),        
    url(r'^product/lanzamientos/$', views.product_lanzamientos, name='product_lanzamientos'),
    url(r'^product/nuevos/$', views.product_nuevos, name='product_nuevos'),
    url(r'^product/rebajados/$', views.product_rebajados, name='product_rebajados'),
    url(r'^product/descatalogados/$', views.product_descatalogados, name='product_descatalogados'),
    url(r'^product/(?P<pk>[0-9]+)/$', views.product_detail, name='product_detail'),
    url(r'^product/(?P<slug>.+)/actualizar/$', views.product_actualizar, name='product_actualizar'),
    url(r'^product/(?P<slug>.+)/anadir/$', views.product_anadir, name='product_anadir'),
    url(r'^product/(?P<slug>.+)/borrar/$', views.product_borrar, name='product_borrar'),
    url(r'^product/(?P<slug>.+)/$', views.product_detail_slug, name='product_detail_slug'), 

    url(r'^search/$', views.product_search, name='product_search'),

    url(r'^ext/(?P<pk>[0-9]+)/$', views.externo_detail, name='externo_detail'),
    url(r'^ext/(?P<pk>[0-9]+)/edit/$', views.externo_edit, name='externo_edit'),
    url(r'^ext/(?P<pk>[0-9]+)/importar/$', views.externo_importar, name='externo_importar'),
    url(r'^ext/(?P<pk>[0-9]+)/procesar_productos/$', views.externo_procesar_productos, name='externo_procesar_productos'),
    url(r'^ext/(?P<pk>[0-9]+)/procesar_imagenes/$', views.externo_procesar_imagenes, name='externo_procesar_imagenes'),
    url(r'^ext/(?P<pk>[0-9]+)/procesar_fabricantes/$', views.externo_procesar_fabricantes, name='externo_procesar_fabricantes'),   
    
    url(r'^cat/$', views.categoria_home, name='categoria_home'),
    
    url(r'^register/$', views.user_register, name='user_register'),
    url(r'^login/$', views.user_login, name='user_login'),
    url(r'^logout/$', views.user_logout, name='user_logout'),

    url(r'^restricted/', views.user_restricted, name='restricted'),

    path('django-project/', RedirectView.as_view(url='https://djangoproject.com'), name='django-project'),
   
    ]    
#   url(r'^ext/(?P<pk>[0-9]+)/procesar_categorias/$', views.externo_procesar_categorias, name='externo_procesar_categorias'), 
#    
#   https://getbootstrap.com/docs/4.0/
#   https://www.w3schools.com/bootstrap4/
#   https://getbootstrap.com/docs/3.3/customize/
#   https://docs.djangoproject.com/en/2.0/
#   https://devcode.la/cursos/
#   https://simpleisbetterthancomplex.com/series/2017/09/25/a-complete-beginners-guide-to-django-part-4.html

#   http://www.louviva.com/    

#   https://grantorrent.net/
#   https://zooqle.com
#   https://www.torrentdownloads.me/

#   https://peliculasyseries.org/