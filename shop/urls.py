from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from . import views
from django.urls import path
from django.views.generic.base import RedirectView
from registration.backends.simple.views import RegistrationView
from registration.backends.default.views import RegistrationView

#if successful at logging
class MyRegistrationView(RegistrationView):
    def get_success_url(self, user):
        return '/myprofile/'

urlpatterns = [
    url(r'^$', views.index, name='index'), 
    
    url(r'^about/$', views.about, name='about'), 
    url(r'^templateshop/$', views.templateshop, name="templateshop"),

    url(r'^cat/$', views.category_home, name='category_home'),
    url(r'^cat/(?P<slug>.+)/$', views.category_detail, name='category_detail'),

	url(r'^fab/$', views.fabricante_home, name='fabricante_home'),
    url(r'^fab/(?P<slug>.+)/$', views.fabricante_detail, name='fabricante_detail'),

    url(r'^ext/$', views.externo_home, name='externo_home'),
    url(r'^ext/init_loadfile/$', views.init_loadfile, name='init_loadfile'),
    url(r'^cron/$', views.externo_cron, name='externo_cron'),
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
    url(r'^ext/(?P<pk>[0-9]+)/procesar_categorias/$', views.externo_procesar_categorias, name='externo_procesar_categorias'),   
    
    url(r'^restricted/', views.user_restricted, name='restricted'),
    url(r'^myprofile/', views.user_myprofile, name='myprofile'),
    url(r'^register/$', views.register, name='register'), 
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),

    path('django-project/', RedirectView.as_view(url='https://djangoproject.com'), name='django-project'),
    path('phpmyadmin/', RedirectView.as_view(url='http://localhost/phpmyadmin/db_structure.php?server=1&db=djangogirls&token=24b7ee8a1e9f702aa5a70f85fcc44d70'), name='phpmyadmin'),
   
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    
    
#   url(r'^accounts/register/$', MyRegistrationView.as_view(), name='registration_register'),
#   url(r'^register/$', views.user_register, name='user_register'),
#   url(r'^login/$', views.user_login, name='user_login'),
#   url(r'^logout/$', views.user_logout, name='user_logout'),    

#   http://www.apuntes-web.es/tag/bootstrap/
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