from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from .models import Product
#from .forms import ProductForm

import xml.etree.ElementTree as ET

def product_list(request):
	products = Product.objects.order_by('-updated')
	return render(request, 'shop/product_list.html', {'products': products})

def product_reload(request):
    path = "static/prueba.xml"
    #etree
    tree = ET.parse(path)
    root = tree.getroot()
    p = Product()
    for product in root:
        print(product.tag, product.attrib, product.text) 
        print(product[0].text)
        p.public_id = product.find('public_id').text
        p.updated = product.find('updated').text
        p.available = product.find('available').text
        p.cost_price = product.find('cost_price').text
        p.price = product.find('price').text
        p.recommended_retail_price = product.find('recommended_retail_price').text
        p.product_url = product.find('product_url').text
        p.title = product.find('title').text
        p.save()
        #print(public_id)
        #for element in product.iter():
            #print(element.tag, element.attrib, element.text)
    #root.getiterator()
    
    return render('product_list')