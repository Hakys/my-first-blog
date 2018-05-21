from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.utils import timezone
from datetime import datetime
from .models import Product, Imagen, Externo, Configuracion
from .forms import ExternoForm
import xml.etree.ElementTree as ET
from django.db import IntegrityError
from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage
from django.core.files.storage import FileSystemStorage
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError  
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_datetime

def product_list(request):
    todo = Imagen.objects.filter(preferred=True).order_by('-product_id__updated')[:15]
    return render(request, 'shop/product_list.html', {'todo':todo})

def product_grid(request):
    todo = Imagen.objects.filter(preferred=True).order_by('-product_id__updated')[:24]
    return render(request, 'shop/product_grid.html', {'todo':todo})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    images = Imagen.objects.filter(product_id__pk=pk).order_by('-preferred')
    return render(request, 'shop/product_detail.html', {'product': product, 'images':images})

def externo_list(request):
    todo = Externo.objects.all().order_by('-updated_date')
    return render(request, 'shop/externo_list.html', {'todo':todo})

def externo_detail(request, pk):
    externo = get_object_or_404(Externo, pk=pk)
    tamano=externo.file.size/1048576
    return render(request, 'shop/externo_detail.html', {'externo': externo,'tamano': tamano})

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

def externo_dreamlove(request):
    name='DreamLoveFile'
    ext = Externo(name=name)
    ext.url='https://store.dreamlove.es/dyndata/exportaciones/csvzip/catalog_1_50_8_0_f2f9102e37db89d71346b15cbc75e8ce_xml_plain.xml'
    ext.importar()
    ext.save()
    return redirect('externo_list')  

def externo_importar(request, pk):
    externo = get_object_or_404(Externo, pk=pk)
    externo.importar()
    externo.save()
    return redirect('externo_detail', pk=externo.pk)

def externo_procesar(request, pk):
    externo = get_object_or_404(Externo, pk=pk)
    tree=ET.parse(externo.path())
    root=tree.getroot() 
    limite=500
    n=0
    nuevo=0
    encontrado=0
    actualizado=0
    imagenes=0
    nuevo_img=0
    actualizado_img=0
    encontrado_img=0
    for prod in root.findall('product'):                  
        if n<limite:
            ref = prod.find('public_id').text
            updated = parse_datetime(prod.find('updated').text)
            try:
                p = Product.objects.get(ref=ref)
                encontrado=encontrado+1
            except ObjectDoesNotExist as e: 
                #Nuevo producto añadido                
                p = Product(ref=ref,updated=datetime.min)
                nuevo=nuevo+1
            if p.updated < updated:
                #try:  
                p.available = prod.find('available').text         
                p.title = prod.find('title').text
                p.cost_price = prod.find('cost_price').text
                p.price = prod.find('price').text
                p.product_url = prod.find('product_url').text  
                p.recommended_retail_price = prod.find('recommended_retail_price').text
                p.default_shipping_cost = prod.find('default_shipping_cost').text
                p.updated = updated
                p.description = prod.find('description').text
                p.html_description = prod.find('html_description').text
                p.delivery_desc= prod.find('delivery_desc').text
                p.vat= prod.find('vat').text
                p.unit_of_measurement= prod.find('unit_of_measurement').text
                p.release_date= prod.find('release_date').text

                p.save() #created_date, 
                actualizado=actualizado+1                
                #except IntegrityError as e:
                #    pass    
                #Imagen.objects.filter(ref=p.ref).delete()       
                for image in prod.find('images'):
                    src = image.find('src').text
                    try:
                        img = Imagen.objects.get(src=src)
                        encontrado_img=encontrado_img+1
                    except ObjectDoesNotExist as e: 
                        #Nueva imagen añadida                
                        img = Imagen(src=src)
                        nuevo_img=nuevo_img+1                        
                    #try:  
                    img.ref = p.ref
                    img.title = p.title 
                    img.name = image.find('name').text        
                    img.product_id = Product.objects.get(ref=p.ref)
                    img.url = image.find('src').text
                    img.preferred = image.get('preferred')
                    img.save()                       
                    #except IntegrityError as e:
                    #    pass 
                    imagenes=imagenes+1
                n=n+1                
    print('Productos'
        +' Procesados: '+str(n)
        +' Encontrados: '+str(encontrado)
        +' Nuevos: '+str(nuevo)
        +' Actualizados: '+str(actualizado)
        +' Total: '+str(encontrado+nuevo)
        )
    print('Imagenes'
        +' Procesadas: '+str(imagenes)
        +' Encontradas: '+str(encontrado_img)
        +' Nuevas: '+str(nuevo_img)        
        +' Actualizadas: '+str(imagenes)
        )
    externo.n_productos=nuevo+encontrado
    externo.n_imagenes=nuevo_img+encontrado_img
    externo.save()
    return redirect('externo_detail', pk=externo.pk)

def product_test(request):
    name='DreamLoveFile'
    ext = Externo.objects.get(name=name)
    tree=ET.parse(ext.path())
    root=tree.getroot() 
    n=0
    buscado = 'D-196688'
    for pro in root.findall('product'):
        ref=pro.find('public_id').text
        n=n+1
        if ref == buscado:
            print(pro.find('title').text)
    print('Numero: '+str(n))
    return redirect('product_list')
    """
    url='https://store.dreamlove.es/dyndata/exportaciones/csvzip/catalog_1_50_8_0_f2f9102e37db89d71346b15cbc75e8ce_xml_plain.xml'
    tree=ET.parse(urlopen(url))
    root=tree.getroot()  
    n=0
    buscado = 'D-196688'
    for pro in root.findall('product'):
        ref=pro.find('public_id').text
        n=n+1
        #if n == 100:
        #    break
        if ref == buscado:
            print(pro.find('title').text)
    print('Numero: '+str(n))
    #xml_data=xml_file.read()
    #xmlDoc = ET.parse( xml_data ) 
    #print(xmlDoct)
    return redirect('product_list')
    """
def product_reload(request):
    #path = "static/store/prueba.xml"
    url='https://store.dreamlove.es/dyndata/exportaciones/csvzip/catalog_1_50_8_0_f2f9102e37db89d71346b15cbc75e8ce_xml_plain.xml'
    tree=ET.parse(urlopen(url))
    root = tree.getroot()#[5]
    for product in root:
        try:
            p = Product()
            #print(product.tag, product.attrib, product.text) 
            #print(product[0].text)
            p.ref = product.find('public_id').text
            p.updated = parse_datetime(product.find('updated').text)
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