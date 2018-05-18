from django.db import models
from django.utils import timezone
import pytz
import datetime
from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage
from django.core.files.storage import FileSystemStorage
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError  

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    ref = models.CharField(max_length=20,unique=True)
    updated = models.DateTimeField('Última Actualización',default=timezone.now)
    available = models.BooleanField('Disponible',default=True)
    title = models.CharField(max_length=200) 
    cost_price = models.DecimalField(max_digits=8,decimal_places=2)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    product_url = models.URLField(blank=True)
    recommended_retail_price = models.DecimalField(max_digits=8,decimal_places=2,default=0)
    #default_shipping_cost = models.DecimalField(decimal_places=2,max_digits=8,default=0)
    #delivery_desc = models.CharField(max_length=20,blank=True)
    #vat = models.DecimalField('IVA',decimal_places=2,max_digits=4,default=21.00)
    #unit_of_measurement = models.CharField(max_length=20,blank=True)
    #description = models.TextField(blank=True)
    #html_description = models.TextField(blank=True)		
    #release_date = models.DateTimeField('Lanzamiento',blank=True, null=True)
    #prepaid_reservation = models.BooleanField('Pre-Pedido',default=False)
    #destocking = models.BooleanField('Liquidación',default=False)
    #shipping_weight_grame = models.IntegerField(default=0)
    #brand = models.CharField(max_length=200,blank=True)
    #sale = models.BooleanField('Rebajado',default=False)
    #new = models.BooleanField('Nuevo',default=True)
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
	#	<stock>
	#		<location path="General">50</location>
	#	</stock>
	#created_date = models.DateTimeField(default=timezone.now)
	#published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        #self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.ref+self.updated.strtime

#fs_media = FileSystemStorage(location='/img')        
        
class Imagen(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    name = models.CharField(max_length=200,blank=True,null=True)
    ref = models.CharField(max_length=20)
    product_id = models.ForeignKey(Product,on_delete=models.CASCADE,null=False)
    #img = models.ImageField(storage=fs)
    src = models.URLField(unique=True,blank=True)
    url = models.URLField(blank=True)
    preferred = models.BooleanField('Portada')
    
    def __str__(self):
        return self.ref          
        
class Externo(models.Model): 
    name = models.CharField(max_length=200)
    url = models.URLField()
    file = models.FileField(null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)  
    updated_date = models.DateTimeField('Última Actualización',default=timezone.now)

    def importar(self):
        request = Request(self.url)
        try:
            response = urlopen(request)
        except HTTPError as e:
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        except URLError as e:
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        else:
            the_file = response.read()
            self.file.save(self.name+str(self.updated_date), the_file, True)  
            self.created_date=timezone.now()
            self.save()        
        return redirect('externo_detail', pk=externo.pk)

    def __str__(self):
        return self.name+str(self.updated_date)
        
    #Storage._open() _save() delete()
    #Storage.exists()
    #Storage.listdir()
    #Storage.size()
    #Storage.url()