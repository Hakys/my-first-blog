from django.db import models
from django.utils import timezone

class Product(models.Model):
	id = models.AutoField(primary_key=True)
	public_id = models.CharField('REFERENCIA',max_length=20)
	updated = models.DateTimeField('Última Actualización',blank=True, null=True)
	#<unit_of_measurement>units</unit_of_measurement>
	available = models.BooleanField()	
	cost_price = models.DecimalField(decimal_places=2,max_digits=8)
	price = models.DecimalField(decimal_places=2,max_digits=8)
	recommended_retail_price = models.DecimalField(decimal_places=2,max_digits=8,blank=True)
	product_url = models.URLField(blank=True)	
	#default_shipping_cost = models.DecimalField(decimal_places=2,max_digits=8)	
	#<delivery_desc>0-24 horas</delivery_desc>
	#<with_serial_number>0</with_serial_number>
	#<min_units_per_order>1</min_units_per_order>
	#<max_units_per_order>999</max_units_per_order>
	#<min_amount_per_order>1</min_amount_per_order>
	#<max_amount_per_order>99999999</max_amount_per_order>
	#vat= models.DecimalField('IVA',decimal_places=2,max_digits=8)
	title = models.CharField(max_length=200)	
	#description = models.TextField()
	#html_description = models.TextField()		
	#release_date = models.DateTimeField(blank=True, null=True)
	#<prepaid_reservation>0</prepaid_reservation>
	#destocking = models.BooleanField()
	#brand = models.CharField(max_length=200)
	#brand_hierarchy = models.TextField()
	#shipping_weight_grame = models.IntegerField()
	
	#	<sale value="0" />
	#	<refrigerated value="0" />
	#	<new value="0" />
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
		return self.title
