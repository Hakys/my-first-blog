import pytz
from datetime import datetime
from decimal import *
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.storage import Storage
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from urllib.error import URLError, HTTPError 
from urllib.request import Request, urlopen

fs_img = FileSystemStorage(location=settings.MEDIA_ROOT)

class Imagen_gen(models.Model):
    title = models.CharField(max_length=200, null=True)
    img = models.ImageField(storage=fs_img, null=True)
    url = models.URLField(unique=True, null=True, blank=True)
    preferred = models.BooleanField('Portada', default=False)
    
    def get_url():
        if self.url:
            return self.url
        else:
            return self.img.url
    
    def __str__(self):
        if self.preferred: 
            preferred='Sí' 
        else: 
            preferred='No'
        return self.title+' ('+preferred+')'

#<categories>
#   <category gesioid="26" ref="Penes Realisticos"><![CDATA[Juguetes XXX|Penes|Penes realisticos]]></category>
#   <category gesioid="129" ref="Especial Gays"><![CDATA[Juguetes XXX|Especial Gays]]></category>
#   <category gesioid="7" ref="Anal"><![CDATA[Juguetes XXX|Anal]]></category>
#</categories>    
class Category(models.Model):
    name = models.CharField(max_length = 150, blank=False)
    slug = models.SlugField(max_length = 150, blank=False)
    activo = models.BooleanField(default = True)
    gesioid = models.IntegerField(unique = True, null = True) 
    parent = models.ForeignKey('self', on_delete = models.SET_NULL, null = True, related_name = 'super_category')
     
    def __str__(self):  
        if self.activo: 
            activo='Si' 
        else: 
            activo='No'         
        full_path = [self.name+' ('+activo+')']                  
        k = self.parent                          
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' >> '.join(full_path[::-1])   

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categorias'  
        unique_together = ('slug', 'parent',)
    
    def get_cat_list(self, separador):
        k = self.parent
        breadcrumb = ["dummy"]
        while k is not None:
            breadcrumb.append(k.slug)
            k = k.parent

        for i in range(len(breadcrumb)-1):
            breadcrumb[i] = separador.join(breadcrumb[-1:i-1:-1])
        return breadcrumb[-1:0:-1]

#image = models.ForeignKey(Imagen_gen,on_delete=models.CASCADE, blank=True, null=True)

#<brand><![CDATA[REALROCK 100% FLESH]]></brand>
#<brand_hierarchy><![CDATA[REAL ROCK|REALROCK 100% FLESH]]></brand_hierarchy>
class Fabricante(models.Model):
    name = models.CharField(max_length = 150, blank=False) 
    slug = models.SlugField(max_length = 150, blank=False)
    activo = models.BooleanField(default = True)
    parent = models.ForeignKey('self', on_delete = models.CASCADE, null = True, related_name = 'children')
    image = models.ForeignKey(Imagen_gen, on_delete = models.CASCADE, blank = True, null = True)

    def __str__(self):  
        if self.activo: 
            activo='Si' 
        else: 
            activo='No'         
        full_path = [self.name+' ('+activo+')']                  
        k = self.parent                          
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' >> '.join(full_path[::-1])    
    
    class Meta:
        unique_together = ('slug', 'parent',)
        ordering = ('name',)
        verbose_name = "Fabricante"
        verbose_name_plural = "Marcas"

    def get_fab_list(self, separador):
        k = self.parent
        breadcrumb = ["dummy"]
        while k is not None:
            breadcrumb.append(k.slug)
            k = k.parent

        for i in range(len(breadcrumb)-1):
            breadcrumb[i] = separador.join(breadcrumb[-1:i-1:-1])
        return breadcrumb[-1:0:-1]

class Product(models.Model): 
    slug = models.SlugField(max_length=150, unique=True, null=False)
    portada = models.ForeignKey(Imagen_gen, on_delete=models.CASCADE,  null=True)
    ref = models.CharField(max_length=30, null=False, unique=True)
    title = models.CharField(max_length=150,  blank=False) 
    description = models.TextField(null=True, blank=True)
    html_description = models.TextField(null=True, blank=True)		
    product_url = models.URLField(max_length=200, null=True, blank=True)

    updated = models.DateTimeField('Última Actualización', default=timezone.now)
    created_date = models.DateTimeField(default=timezone.now)
    release_date = models.DateTimeField('Lanzamiento', blank=True, null=True)

    available = models.BooleanField('Disponible', default=True)
    destocking = models.BooleanField('Liquidación', default=False)    
    sale = models.BooleanField('Rebajado', default=False)
    new = models.BooleanField('Nuevo', default=True)

    cost_price = models.DecimalField(max_digits=8, decimal_places=2)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    recommended_retail_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    default_shipping_cost = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    delivery_desc = models.CharField(max_length=20, blank=True)
    vat = models.DecimalField('IVA',decimal_places=2, max_digits=4, default=21.00)
    unit_of_measurement = models.CharField(max_length=20, blank=True)
    pvp = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    fabricante = models.ForeignKey(Fabricante, on_delete=models.SET_NULL, null=True)

    #<stock><location path="General">50</location></stock>
    stock = models.IntegerField(default=0)

    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, related_name='category_ppal')
    categories = models.ManyToManyField(Category)

    #prepaid_reservation = models.BooleanField('Pre-Pedido',default=False)
    #shipping_weight_grame = models.IntegerField(default=0)
    #brand = models.CharField(max_length=200,blank=True)
    #<min_units_per_order>1</min_units_per_order>
	#<max_units_per_order>999</max_units_per_order>
	#<min_amount_per_order>1</min_amount_per_order>
	#<max_amount_per_order>99999999</max_amount_per_order>    
    #brand_hierarchy = models.TextField()
	#	<refrigerated value="0" />
	#	<barcodes>
	#		<barcode type="EAN-13"><![CDATA[697309010016]]></barcode>
	#	</barcodes>
    #	<categories>
	#		<category gesioid="87" ref="Aceites Esenciales"><![CDATA[Aceites y Lubricantes|Aceites y Cremas de masaje|Aceites esenciales]]></category>
	#		<category gesioid="94" ref="Efecto Afrodisiaco"><![CDATA[Aceites y Lubricantes|Aceites y Cremas de masaje|Efecto afrodisiaco]]></category>
	#		<category gesioid="91" ref="Clima Erotico"><![CDATA[Aceites y Lubricantes|Aceites y Cremas de masaje|Clima erótico]]></category>
	#		<category gesioid="88" ref="100% comestibles"><![CDATA[Aceites y Lubricantes|Aceites y Cremas de masaje|100% comestibles]]></category>
	#		<category gesioid="77" ref="Aceites y Cremas de masaje"><![CDATA[Aceites y Lubricantes|Aceites y Cremas de masaje]]></category>
	#	</categories>
	#	<internationalization>
	#		<title><value lang="en-UK"><![CDATA[SHUNGA EROTIC MASSAGE OIL DESIRE]]></value></title>
	#		<description><value lang="en-UK"><![CDATA[SHUNGA EROTIC MASSAGE OIL DESIRE]]></value></description>
	#		<html_description><value lang="en-UK"><![CDATA[<p>Enjoy the pleasures of giving or receiving a sensual, erotic massage using Shunga&#39;s exclusive blend of cold-pressed oil made from almond oil, grapeseed oil, sesame seed oil, avocado oil, vitamin E, essential oil safflower oil, extracts of ylang-ylang and yohimbe, and depending on the fragrance, essential oil extracts from lavender, rose blossoms, peach blossoms, apple blossoms, orange blossoms, and vanilla.</p><p>These oils were carefully selected for their stimulating and energizing qualities. They slide smoothly and easily over your skin. No greasy sensations!</p><p>Plus, an exotic fragrance will bring your senses to peak pleasure.</p><ul>	<li>250 ml</li></ul>]]></value></html_description>
	#	</internationalization>
	#	<images scope="all">
	#		<image preferred="1">
	#			<name><![CDATA[]]></name>
	#			<src>https://store.dreamlove.es/productos/imagenes/img_9450_56829edf85f00d98b60692dfeb77ae53_1.jpg</src>
	#		</image>
	#	</images>
	#published_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        #fab_list = ''
        #if self.get_fab_list(' -> '):
        fab_list = ' {0}'.format(self.get_fab_list(' -> '))
        return '{0}{1} ({2})'.format(self.ref,fab_list,self.updated)
    
    class Meta:
        ordering = ('-release_date',)
    
    def publish(self):
        #self.published_date = timezone.now()
        self.available = True
        self.save()
    
    def get_fab_list(self, separador):
        k = self.fabricante
        breadcrumb = ["dummy"]
        while k is not None:
            breadcrumb.append(k.slug)
            k = k.parent

        for i in range(len(breadcrumb)-1):
            breadcrumb[i] = separador.join(breadcrumb[-1:i-1:-1])
        return breadcrumb[-1:0:-1]    

    def get_pvp(self):
        beneficio = Configuracion.objects.get(variable='beneficio').get_valor_dec()
        rec_equivalencia = Configuracion.objects.get(variable='rec_equivalencia').get_valor_dec()
        if not self.vat:
            iva = Configuracion.objects.get(variable='iva').get_valor_dec()
        else:
            iva = Decimal(self.vat)
        iva=iva/100
        req=Decimal(rec_equivalencia/1000)
        porc_benef=Decimal(beneficio/100)
        cost_price = Decimal(self.cost_price)
        coste_total=cost_price+cost_price*iva+cost_price*req
        self.pvp = round(coste_total/(1-porc_benef),2)
        return self.pvp

#fs_media = FileSystemStorage(location=STATIC_ROOT+'/img')  
class Imagen(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    ref = models.CharField(max_length=20, blank=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, null=False)
    #img = models.ImageField(storage=fs)
    src = models.URLField(unique=True)
    url = models.URLField(blank=True)
    preferred = models.BooleanField('Portada', default=False)
    
    def __str__(self):
        if self.preferred: 
            preferred='Sí' 
        else: 
            preferred='No'
        return self.ref+' '+self.title+' ('+preferred+')'    
    
    def exist(image_url):
        if urlopen(image_url):
            return True
        else:
            return False

fs = FileSystemStorage(location=settings.STATIC_ROOT+'/store')

class Externo(models.Model): 
    name = models.CharField(max_length=200, unique=True)
    url = models.URLField()
    file = models.FileField(storage=fs, null=True, blank=True)
    created_date = models.DateTimeField('Fecha de Creación', default=timezone.now)  
    updated_date = models.DateTimeField('Última Actualización', default=datetime.min)
    n_productos = models.IntegerField(default=0)
    n_fabricantes = models.IntegerField(default=0)
    n_imagenes = models.IntegerField(default=0)
    n_categorias = models.IntegerField(default=0)

    def importar(self):
        try:
            response = urlopen(self.url)
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: '+e.code)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: '+e.reason)
        
        else:      
            fecha = datetime.now().strftime("%Y%m%d-%H%M")
            extension = self.url.split('.')[-1]
            self.file.save(self.name+'_'+fecha+'.'+extension, response)    
            self.updated_date=timezone.now()
            Product.objects.all().update(updated=datetime.min)
            self.n_productos=0
            self.n_fabricantes=0
            self.n_imagenes=0
            self.n_categorias=0
            self.save()   

    def path(self):
        return self.file.path

    def __str__(self):
        return self.file.name+' ('+str(self.updated_date)+')'

class Configuracion(models.Model):
    variable = models.CharField(max_length=200, null=False, unique=True)
    valor = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        if self.activo: 
            activo='Si' 
        else: 
            activo='No'
        valor=''
        if self.valor: 
            valor=': '+self.valor   
        return self.variable+valor+' ('+activo+')'
    
    def get_valor_int(self):
        if self.activo:
            return int(self.valor)
        else:
            return False

    def get_valor(self):
        if self.activo:
            return str(self.valor)
        else:
            return False
 
    def get_valor_dec(self):
        if self.activo:
            return Decimal(self.valor)
        else:
            return False

class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)

    # The additional attributes we wish to include.
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username
