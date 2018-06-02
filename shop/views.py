from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.utils import timezone
from django.utils.text import slugify
from datetime import datetime
from django.db import models, IntegrityError
from django.db.models import Q
from .models import * #Product, Imagen, Imagen_gen, Externo, Configuracion, Fabricante #, Categoria
from .forms import ExternoForm
import xml.etree.ElementTree as ET
from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage, FileSystemStorage
from urllib.request import Request, urlopen, URLError, HTTPError  
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_datetime
from django.http import HttpResponse

def product_list(request):
    todo = Imagen.objects.filter(preferred=True).order_by('-product_id__release_date')[:15]
    return render(request, 'shop/product_list.html', {'todo':todo})

def product_grid(request):
    fichas = Imagen.objects.filter(preferred=True).order_by('-product_id__release_date')[:24]  
    return render(request, 'shop/product_grid.html',{
        'fichas': fichas,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, Q(pk=pk)|Q(ref=pk)|Q(slug=pk))
    images = Imagen.objects.filter(product_id__pk=product.pk).order_by('-preferred')
    breadcrumbs_link = product.get_fab_list()
    fabricante_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link]
    breadcrumbs = zip(breadcrumbs_link, fabricante_name)
    return render(request, 'shop/product_detail.html', {'product': product, 'images':images, 'breadcrumbs':breadcrumbs})

def product_search(request):
    fichas=None
    if request.method == 'POST':
        search_text = request.POST['search_text']
        if search_text:
            fichas = Imagen.objects.filter(preferred=True, 
                product_id__in=Product.objects.filter(
                    Q(ref__contains=search_text) |
                    Q(title__contains=search_text) |
                    Q(description__contains=search_text) |
                    Q(html_description__contains=search_text)
                    )
                )[:30]
    return render_to_response('shop/ajax_search.html', {'fichas': fichas})

def externo_list(request):
    todo = Externo.objects.all().order_by('-updated_date')
    if len(todo)==1:
        return externo_detail(request, todo[0].pk)
    else:
        return render(request, 'shop/externo_list.html', {'todo':todo})

def externo_detail(request, pk):
    externo = get_object_or_404(Externo, pk=pk)
    externo.n_productos = len(Product.objects.all())
    externo.n_fabricantes = len(Fabricante.objects.all())
    externo.n_imagenes = len(Imagen.objects.all())
    #externo.n_categorias = len(Categoria.objects.all())
    externo.save()
    context = {
        'tamano' : externo.file.size/1048576,
    }
    return render(request, 'shop/externo_detail.html', {'externo': externo,'context': context})

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

def externo_cron(request):
    try:
        ext = Externo.objects.get(name='DreamLoveFile')
    except ObjectDoesNotExist as e:
        externo_dreamlove(request)
        ext = get_object_or_404(Externo, name='DreamLoveFile')
    
    tree=ET.parse(ext.path())
    root=tree.getroot() 
    #print('.'+str(proc.get('retorno')))
    if not procesar_productos(root).get('retorno'): 
        print('Productos Hecha')
        if not procesar_fabricantes(root).get('retorno'): 
            print('Fabricantes Hecha')
            if not procesar_imagenes(root).get('retorno'):  
                print('Imagenes Hecha')
                salida=0
            else:
                salida=-3
        else:
            salida=-2
    else:
        salida=-1
    ext.n_productos = len(Product.objects.all())
    ext.n_fabricantes = len(Fabricante.objects.all())
    ext.n_imagenes = len(Imagen.objects.all())
    #externo.n_categorias = len(Categoria.objects.all())
    ext.save()
    '''
    context = {
        'externo': externo,
        'tamano': externo.file.size/1048576,
        'salida': salida['salida'],
    }
    return render(request, 'shop/externo_detail.html', context) 
    '''
    return HttpResponse(salida)

def procesar_productos(root):
    if root:
        limite=int(get_object_or_404(Configuracion, variable='product_limite').valor)
        n=0
        nuevo=0
        encontrado=0
        actualizado=0
        imagenes=0
        nuevo_img=0
        actualizado_img=0
        encontrado_img=0
        error=0
        salida=''
        for prod in root.findall('product'):
            if actualizado<limite:
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
                    try:
                        if prod.find('title').text:
                            p.title = prod.find('title').text                
                        else:
                            if prod.find('description').text:
                                p.title = prod.find('description').text
                            else:    
                                if prod.find('internationalization/title/value').text:
                                    p.title = prod.find('internationalization/title/value').text
                                else: 
                                    if prod.find('internationalization/description/value').text:
                                        p.title = prod.find('internationalization/description/value').text
                                    else: 
                                        p.title = p.ref
                        p.description = p.title
                        p.slug=slugify(p.title)
                        p.available = prod.find('available').text  
                        p.cost_price = prod.find('cost_price').text
                        p.price = prod.find('price').text
                        p.product_url = prod.find('product_url').text  
                        p.recommended_retail_price = prod.find('recommended_retail_price').text
                        p.default_shipping_cost = prod.find('default_shipping_cost').text
                        p.updated = updated                    
                        p.html_description = prod.find('html_description').text
                        p.delivery_desc= prod.find('delivery_desc').text
                        p.vat= prod.find('vat').text
                        p.unit_of_measurement= prod.find('unit_of_measurement').text
                        p.release_date= prod.find('release_date').text
                        
                        p.save() #created_date, 
                        actualizado=actualizado+1                
                    except IntegrityError as e:    
                        #print('ERROR REF: '+p.ref)  
                        error=error+1  
                        pass  
                n=n+1  
            else:
                break              
        return {
            'retorno': actualizado, 
            'salida': '<br> Productos Procesados: '+str(n)
                +'<br> Encontrados: '+str(encontrado)
                +'<br> Nuevos: '+str(nuevo)
                +'<br> Actualizados: '+str(actualizado)
                +'<br> Errores: '+str(error)
                +'<br> Total: '+str(encontrado+nuevo)
            }
    else:
        return {
            'retorno':-1,
            'salida': "no root"
            }

def externo_procesar_productos(request, pk):
    externo = get_object_or_404(Externo, pk=pk)
    tree=ET.parse(externo.path())
    root=tree.getroot() 
    salida=procesar_productos(root)
    externo.n_productos = len(Product.objects.all())
    #externo.n_fabricantes = len(Fabricante.objects.all())
    #externo.n_imagenes = len(Imagen.objects.all())
    #externo.n_categorias = len(Categoria.objects.all())
    externo.save()
    context = {
        'externo': externo,
        'tamano': externo.file.size/1048576,
        'salida': salida['salida'],
    }
    return render(request, 'shop/externo_detail.html', context) 

def procesar_imagenes(root):
    if root:
        limite=int(Configuracion.objects.get(variable='imagen_limite').valor)
        n=0
        nuevo=0
        productos=0
        encontrada=0
        nuevo_img=0
        procesada=0
        error_img=0
        actualizada=0
        for prod in root.findall('product'):
            if nuevo_img<limite:
                ref = prod.find('public_id').text
                updated = parse_datetime(prod.find('updated').text)
                try:
                    p = Product.objects.get(ref=ref)
                    productos=productos+1
                except ObjectDoesNotExist as e:
                    p = None
                    pass
                if p:
                    #Imagen.objects.filter(ref=p.ref).delete()       
                    for image in prod.find('images'):                    
                        if image.find('src').text:
                            src = image.find('src').text
                            try:
                                img = Imagen.objects.get(src=src)
                            except ObjectDoesNotExist as e:             
                                img = Imagen(src=src)
                            if img.ref:                                
                                encontrada=encontrada+1
                            else: 
                                #Nueva imagen añadida 
                                try:  
                                    img.ref = p.ref
                                    img.title = p.title      
                                    if image.find('name').text :
                                        img.name = p.title
                                    else:
                                        img.name = image.find('name').text
                                    img.product_id = p
                                    img.url = image.find('src').text
                                    img.preferred = image.get('preferred')
                                    img.save()  
                                    nuevo_img=nuevo_img+1                     
                                except IntegrityError as e:
                                    print('ERROR REF: '+p.ref)  
                                    print('ERROR SCR: ')
                                    print(image.find('src'))  
                                    error_img=error_img+1 
                                    pass                                
                            procesada=procesada+1
                n=n+1 
            else:
                    break               
        return {
            'retorno': nuevo_img, 
            'salida': '<br> Productos Procesados: '+str(n)+' -> '+str(productos)
                +'<br> Imagenes Procesadas: '+str(procesada)
                +'<br> Encontradas: '+str(encontrada)
                +'<br> Nuevos: '+str(nuevo_img)
                +'<br> Actualizadas: '+str(actualizada)
                +'<br> Errores: '+str(error_img)
                +'<br> Total: '+str(encontrada+nuevo+error_img)
            }
    else:
        return {
            'retorno':-1,
            'salida': "no root"
            }

def externo_procesar_imagenes(request, pk):
    externo = get_object_or_404(Externo, pk=pk)
    tree=ET.parse(externo.path())
    root=tree.getroot() 
    salida=procesar_imagenes(root)
    #externo.n_productos = len(Product.objects.all())
    #externo.n_fabricantes = len(Fabricante.objects.all())
    externo.n_imagenes = len(Imagen.objects.all())
    #externo.n_categorias = len(Categoria.objects.all())
    externo.save()
    context = {
        'externo': externo,
        'tamano': externo.file.size/1048576,
        'salida': salida['salida'],
    }
    return render(request, 'shop/externo_detail.html', context) 

def procesar_fabricantes(root):
    if root:
        limite=int(Configuracion.objects.get(variable='fabricante_limit').valor)
        n=0
        nuevo=0
        encontrado=0
        actualizado=0
        imagenes=0
        nuevo_img=0
        actualizado_img=0
        encontrado_img=0
        error=0
        parent_ppal=None
        for prod in root.findall('product'):        
            if nuevo<limite: 
                ref = prod.find('public_id').text
                #<brand_hierarchy><![CDATA[REAL ROCK|REALROCK 100% FLESH]]></brand_hierarchy>
                try:
                    if prod.find('brand_hierarchy').text:
                        fabricante_jerarquia = prod.find('brand_hierarchy').text  
                        parent = None  
                        for fab_name in fabricante_jerarquia.split('|'):
                            if fab_name:
                                name=fab_name
                            else:
                                name = 'Diabla Roja'
                                error=error+1
                            parent_ppal=parent
                            try:
                                fab = Fabricante.objects.get(name=name, parent=parent)
                                encontrado=encontrado+1
                            except ObjectDoesNotExist as e: 
                                #Nuevo añadido                
                                fab = Fabricante(name=name, slug=slugify(name), parent=parent)
                                fab.save()
                                nuevo=nuevo+1   
                            parent = fab
                except:
                    error=error+1
                #<brand><![CDATA[REALROCK 100% FLESH]]></brand>                
                try:
                    if prod.find('brand').text:
                        fab_name = prod.find('brand').text
                except:
                    fab_name = 'Diabla Roja'
                    error=error+1
                try:
                    fab = Fabricante.objects.get(name=fab_name)
                    encontrado=encontrado+1
                except ObjectDoesNotExist as e: 
                    #Nuevo añadido                
                    fab = Fabricante(name=fab_name, slug=fab_name, parent=parent_ppal)
                    fab.save()
                    nuevo=nuevo+1   
                try:
                    p = Product.objects.get(ref=ref)
                    if p:
                        p.fabricante = Fabricante.objects.get(pk=fab.pk)
                        p.save()
                    else:
                        error=error+1
                except ObjectDoesNotExist as e:
                    error=error+1
                '''
                    parent=Categoria.objects.get(gesioid=0)
                    for categoria in prod.find('categories'):
                        name = categoria.attrib['ref']
                        gesioid = categoria.attrib['gesioid']
                    
                        for cat_name in categoria.text.split('|'):
                            try:
                                c = Categoria(name=cat_name)
                                #c.image = Imagen_gen(title=name,url=prod.find('images/image/src').text)
                                #c.image.save()
                                c.parent = parent
                                c.save()
                                parent = c
                            except IntegrityError as e:
                                #print(str(gesioid)+' '+name)
                                pass
                        try:                        
                            c = Categoria(name=name)
                            #c.image = Imagen_gen(title=name,url=prod.find('images/image/src').text)
                            #c.image.save()
                            c.parent = parent
                            c.save()                    
                        except IntegrityError as e:
                            #print(str(gesioid)+' '+name)
                            pass 
                    '''
                n=n+1 
            else:
                break              
        return {
            'retorno': nuevo, 
            'salida': '<br> Productos Procesados: '+str(n)
                +'<br> Fabricantes Encontradas: '+str(encontrado)
                +'<br> Nuevos: '+str(nuevo)
                +'<br> Actualizadas: '+str(actualizado)
                +'<br> Errores: '+str(error)
                +'<br> Total: '+str(encontrado+nuevo)
            }
    else:
        return {
            'retorno':-1,
            'salida': "no root"
            }

def externo_procesar_fabricantes(request, pk):
    externo = get_object_or_404(Externo, pk=pk)
    tree=ET.parse(externo.path())
    root=tree.getroot() 
    salida = procesar_fabricantes(root)
    #externo.n_productos = len(Product.objects.all())
    externo.n_fabricantes = len(Fabricante.objects.all())
    #externo.n_imagenes = len(Imagen.objects.all())
    #externo.n_categorias = len(Categoria.objects.all())
    externo.save()
    context = {
        'externo': externo,
        'tamano': externo.file.size/1048576,
        'salida': salida['salida'],
    }
    return render(request, 'shop/externo_detail.html', context) 

def templateshop(request):
    return render(request,"shop/templateshop.html")

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

def fabricante_list(request):
    fabricantes = Fabricante.objects.filter(parent=None)
    return render(request,"shop/fabricante_list.html",{
        'lista':fabricantes,
    })
'''
def fabricante_detail(request,slug):
    
    fabricante = Fabricante.objects.filter(slug=slug)
    salida ='Fabricante'
    context = {
        'fabricante': fabricante,
        'salida': salida,
    }
    return render(request, 'shop/fabricante_detail.html', context)
'''
def fabricante_show(request,hierarchy= ''):      
    fabricante_slug = hierarchy.split('/')
    fabricantes = Fabricante.objects.all().order_by('name')
    fabricante_queryset = list(fabricantes)
    all_slugs = [ x.slug for x in fabricante_queryset ]
    parent = None
    for slug in fabricante_slug:
        if slug in all_slugs:
            parent = get_object_or_404(Fabricante,slug=slug,parent=parent)
        else:
            product = get_object_or_404(Product, Q(pk=slug)|Q(ref=slug)|Q(slug=slug))
            breadcrumbs_link = product.get_fab_list()
            fabricante_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link]
            breadcrumbs = zip(breadcrumbs_link, fabricante_name)
            images = Imagen.objects.filter(product_id__pk=product.pk).order_by('-preferred')
            return render(request, 'shop/product_detail.html', {
                'product': product, 
                'images':images,
                'breadcrumbs':breadcrumbs,                
            })
    
    #'sub_fabricantes':children,children = Fabricante.objects.filter(parent__slug=parent.slug)
    fichas = Imagen.objects.filter(preferred=True, product_id__fabricante=parent).order_by('-product_id__updated')
    sub_fabricantes = parent.children.all()
    return render(request, "shop/fabricante_detail.html", {
        'ficha':parent,
        'fichas_prod': fichas,
        'sub_fabricantes': sub_fabricantes,
    })
   
    '''
    def show_category(request,hierarchy= None):
    category_slug = hierarchy.split('/')
    category_queryset = list(Category.objects.all())
    all_slugs = [ x.slug for x in category_queryset ]
    parent = None
    for slug in category_slug:
        if slug in all_slugs:
            parent = get_object_or_404(Category,slug=slug,parent=parent)
        else:
            instance = get_object_or_404(Post, slug=slug)
            breadcrumbs_link = instance.get_cat_list()
            category_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link]
            breadcrumbs = zip(breadcrumbs_link, category_name)
            return render(request, "postDetail.html", {'instance':instance,'breadcrumbs':breadcrumbs})

    return render(request,"categories.html",{'post_set':parent.post_set.all(),'sub_categories':parent.children.all()})
    '''