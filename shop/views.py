from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from .models import Product, Imagen, Externo
from .forms import ExternoForm
import xml.etree.ElementTree as ET
#from django.db.models import Subquery
from django.db import IntegrityError
#from django.shortcuts import render_to_response

from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage
from django.core.files.storage import FileSystemStorage
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError  

def product_list(request):
    todo = Imagen.objects.filter(preferred=True).order_by('-product_id__updated')[:12]
    #print(todo)
    return render(request, 'shop/product_list.html', {'todo':todo})

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'shop/product_detail.html', {'product': product})

def externo_list(request):
    todo = Externo.objects.all()
    #print(todo)
    return render(request, 'shop/externo_list.html', {'todo':todo})

def externo_detail(request, pk):
    externo = get_object_or_404(Externo, pk=pk)
    return render(request, 'shop/externo_detail.html', {'externo': externo})

def externo_dreamlove(request):
    name='Dream Love'
    ext = Externo(name=name)
    ext.url='https://store.dreamlove.es/dyndata/exportaciones/csvzip/catalog_1_50_8_0_f2f9102e37db89d71346b15cbc75e8ce_xml_plain.xml'
    ext.importar()
    ext.save()
    return redirect('externo_list')

def externo_importar(request, pk):
    externo = get_object_or_404(Externo, pk=pk)
    externo.importar()
    return redirect('externo_detail', pk=externo.pk)

def externo_edit(request, pk):
    externo = get_object_or_404(Externo, pk=pk)
    if request.POST:
        form = ExternoForm(request.POST,instance=externo)
        if form.is_valid():
            request = Request(form.instance.url)
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
                form.instance.file.save(form.instance.name, the_file, True)  
                form.instance.save()        
                return redirect('externo_detail', pk=externo.pk)
    else:
        form = ExternoForm(instance=externo)
    return render(request, 'shop/externo_edit.html', {'form': form})

def product_test(request):
    return redirect('product_list') 
    
def product_reload(request):
    path = "static/store/prueba.xml"
    tree = ET.parse(path)
    root = tree.getroot()#[5]
    for product in root:
        try:
            p = Product()
            #print(product.tag, product.attrib, product.text) 
            #print(product[0].text)
            p.ref = product.find('public_id').text
            p.updated = product.find('updated').text
            p.available = product.find('available').text         
            p.title = product.find('title').text
            p.cost_price = product.find('cost_price').text
            p.price = product.find('price').text
            p.product_url = product.find('product_url').text  
            p.recommended_retail_price = product.find('recommended_retail_price').text
            p.save() 
        except IntegrityError as e:
            pass    
        #Imagen.objects.filter(ref=p.ref).delete()       
        for image in product.find('images'):
            try:  
                img = Imagen()
                img.src = image.find('src').text
                img.ref = p.ref
                img.title = p.title 
                img.name = image.find('name').text        
                img.product_id = Product.objects.get(ref=p.ref)
                img.url = image.find('src').text
                img.preferred = image.get('preferred')
                img.save()
            except IntegrityError as e:
                pass
        #print(public_id)
        #for element in product.iter():
            #print(element.tag, element.attrib, element.text)
        #root.getiterator()
    return redirect('product_list')