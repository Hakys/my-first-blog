from .models import *
from .forms import ExternoForm
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.utils import timezone
from django.utils.text import slugify
from django.utils.dateparse import parse_datetime
from datetime import datetime
from django.db import models, IntegrityError
from django.db.models import Q
import xml.etree.ElementTree as ET
from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage, FileSystemStorage
from urllib.request import Request, urlopen, URLError, HTTPError  
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

def init_loaddata(request):
    salida=0
    try:    
        obj = Configuracion(variable='dto_mayorista', valor='10', activo=True)
        obj.save()
    except IntegrityError as e:
        print(obj, e)
    try:    
        obj = Configuracion(variable='beneficio', valor='60', activo=True)
        obj.save()
    except IntegrityError as e:
        print(obj, e)
    try:    
        obj = Configuracion(variable='product_limite', valor='500', activo=True)
        obj.save()
    except IntegrityError as e:
        print(obj, e)
    try:    
        obj = Configuracion(variable='imagen_limite', valor='1000', activo=True)
        obj.save()
    except IntegrityError as e:
        print(obj, e)
    try:    
        obj = Configuracion(variable='fabricante_limite', valor='500', activo=True)
        obj.save()
    except IntegrityError as e:
        print(obj, e)
    try:    
        obj = Configuracion(variable='prod_page', valor='24', activo=True)
        obj.save()
    except IntegrityError as e:
        print(obj, e)
    try:    
        obj = Configuracion(variable='prod_home', valor='24', activo=True)
        obj.save()
    except IntegrityError as e:
        print(obj, e)
    try:    
        obj = Configuracion(variable='run_cron',valor='',activo=True)    
        obj.save()
    except IntegrityError as e:
        print(obj, e)
    try:    
        obj = Fabricante(name='DIABLA ROJA', slug=slugify('DIABLA ROJA'), parent=None)
        obj.save() 
    except IntegrityError as e:
        print(obj, e)
    return salida

def categoria_home(request):
    return redirect('product_home')

def product_list(request):
    todo = Imagen.objects.filter(preferred=True).order_by('-product_id__release_date')    
    prod_page=int(Configuracion.objects.get(variable='prod_page').valor)
    #print(prod_page)
    paginator = Paginator(todo, prod_page)
    page = request.GET.get('page')
    todo_paginado = paginator.get_page(page)
    return render(request, 'shop/product_list.html', {'todo':todo_paginado})

def product_home(request):
    fichas_prod = Imagen.objects.filter(preferred=True,product_id__new=True).order_by('-product_id__release_date')[:24]  
    return render(request, 'shop/product_cat.html',{
        'title':'Próximos Lanzamientos',
        'fichas_prod': fichas_prod,
    })

def product_nuevos(request):
    todo = Imagen.objects.filter(preferred=True,product_id__new=True).order_by('-product_id__created_date')    
    prod_page=int(Configuracion.objects.get(variable='prod_page').valor)
    paginator = Paginator(todo, prod_page)
    page = request.GET.get('page')
    todo_paginado = paginator.get_page(page)
    return render(request, 'shop/product_cat.html',{
        'title':'Novedades',
        'fichas_prod': todo_paginado,
    })

def product_rebajados(request):
    todo = Imagen.objects.filter(preferred=True,product_id__sale=True).order_by('-product_id__created_date')    
    prod_page=int(Configuracion.objects.get(variable='prod_page').valor)
    paginator = Paginator(todo, prod_page)
    page = request.GET.get('page')
    todo_paginado = paginator.get_page(page)
    return render(request, 'shop/product_cat.html',{
        'title':'Rebajados',
        'fichas_prod': todo_paginado,
    })

def product_descatalogados(request):
    todo = Imagen.objects.filter(preferred=True,product_id__destocking=True).order_by('-product_id__created_date')    
    prod_page=int(Configuracion.objects.get(variable='prod_page').valor)
    paginator = Paginator(todo, prod_page)
    page = request.GET.get('page')
    todo_paginado = paginator.get_page(page)
    return render(request, 'shop/product_cat.html',{
        'title':'Descatalogados',
        'fichas_prod': todo_paginado,
    })

def product_detail(request, pk, salida=[]):
    product = get_object_or_404(Product, pk=pk)
    images = Imagen.objects.filter(product_id__pk=product.pk).order_by('-preferred')
    breadcrumbs_link = product.get_fab_list('/')
    fabricante_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link]
    breadcrumbs = zip(breadcrumbs_link, fabricante_name)
    beneficio=int(get_object_or_404(Configuracion, variable='beneficio').valor)
    
    return render(request, 'shop/product_detail.html', {
        'product': product, 
        'price': product.price*product.vat/100,
        'cost_price': product.cost_price*product.vat*beneficio/100,
        'recommended_retail_price': product.recommended_retail_price*product.vat/100,
        'images':images, 
        'breadcrumbs':breadcrumbs,
        'salida':salida,
        })

def product_detail_slug(request, slug):
    salida=[]
    product = get_object_or_404(Product, Q(ref=slug)|Q(slug=slug))
    images = Imagen.objects.filter(product_id__pk=product.pk).order_by('-preferred')
    breadcrumbs_link = product.get_fab_list('/')
    fabricante_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link]
    breadcrumbs = zip(breadcrumbs_link, fabricante_name)
    beneficio=int(get_object_or_404(Configuracion, variable='beneficio').valor)
    dto_mayorista=int(get_object_or_404(Configuracion, variable='dto_mayorista').valor)
    #print('popo'+product)
    product.default_shipping_cost+=product.default_shipping_cost*(product.vat/100)
    return render(request, 'shop/product_detail.html', {
        'product': product, 
        'price': product.price,
        'cost_price': product.cost_price-product.cost_price*dto_mayorista/100,
        'recommended_retail_price': product.recommended_retail_price,
        'images':images, 
        'breadcrumbs':breadcrumbs,
        'salida': salida,
        })

def product_actualizar(request, slug):
    externo = get_object_or_404(Externo, name='DreamLoveFile')
    tree=ET.parse(externo.path())
    root=tree.getroot()
    producto = Product.objects.filter(Q(ref=slug)|Q(slug=slug))
    lista=[p.ref for p in producto]
    for prod in root.findall('product'):
        ref = prod.find('public_id').text
        if not ref in lista:
            root.remove(prod)
        #else:
            #ET.dump(prod)
    salida=[]
    salida.append(procesar_productos(root))
    salida.append(procesar_fabricantes(root))  
    salida.append(procesar_imagenes(root))
    return redirect('/product/'+slug+'/', salida)

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
    externo.n_productos = Product.objects.all().count()
    externo.n_fabricantes = Fabricante.objects.all().count()
    externo.n_imagenes = Imagen.objects.all().count()
    #externo.n_categorias = len(Categoria.objects.all())
    externo.save()
    return render(request, 'shop/externo_detail.html', {
        'externo': externo,
        'tamano' : externo.file.size/1048576,
        'no_updated' :  Product.objects.filter(updated=datetime.min).count(),
        })

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
        run_cron=Configuracion.objects.get(variable='run_cron')
    except ObjectDoesNotExist as e:
        init_loaddata(request)
        run_cron=Configuracion.objects.get(variable='run_cron')
    if run_cron.activo:
        try:
            ext = Externo.objects.get(name='DreamLoveFile')
        except ObjectDoesNotExist as e:
            externo_dreamlove(request)
            ext = get_object_or_404(Externo, name='DreamLoveFile')
        tree=ET.parse(ext.path())
        root=tree.getroot() 
        if not procesar_productos(root).get('retorno'): 
            if not procesar_fabricantes(root).get('retorno'): 
                if not procesar_imagenes(root).get('retorno'):  
                    ext.importar()
                    ext.save()
                    salida=0
                else:
                    salida=-1
            else:
                salida=-2
        else:
            salida=-3
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
    else:
        salida=-4
    return HttpResponse({'Error nivel:',salida})

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
                        p.slug = slugify(p.title)
                        p.available = prod.find('available').text  
                        p.cost_price = prod.find('cost_price').text
                        p.price = prod.find('price').text
                        p.product_url = prod.find('product_url').text  
                        p.recommended_retail_price = prod.find('recommended_retail_price').text
                        p.default_shipping_cost = prod.find('default_shipping_cost').text
                        p.updated = updated                    
                        p.html_description = prod.find('html_description').text
                        p.delivery_desc = prod.find('delivery_desc').text
                        p.vat = prod.find('vat').text
                        p.unit_of_measurement = prod.find('unit_of_measurement').text
                        p.release_date = prod.find('release_date').text
                        p.destocking = prod.find('destocking').text   
                        p.sale = prod.find('sale').attrib['value']
                        p.new = prod.find('new').attrib['value']
                        #<stock><location path="General">50</location></stock>
                        stock = prod.find('stock')
                        p.stock = stock.find('location').text

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
            'retorno': -1,
            'salida': "no root"
            }

def externo_procesar_productos(request, pk):
    externo = get_object_or_404(Externo, pk=pk)
    tree=ET.parse(externo.path())
    root=tree.getroot() 
    salida=procesar_productos(root)
    externo.n_productos = len(Product.objects.all())
    #externo.n_categorias = len(Categoria.objects.all())
    externo.save() 
    return render(request, 'shop/externo_detail.html', {
        'externo': externo,
        'tamano': externo.file.size/1048576,
        'salida': [salida],
    }) 

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
                    Imagen.objects.filter(ref=p.ref).delete()       
                    for image in prod.find('images'):                    
                        if Imagen.exist(image.find('src').text):
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
                                    '''
                                    if img.preferred:
                                        p.portada = Imagen.objects.get(pk=img.pk) 
                                        p.save()     
                                    '''
                                    nuevo_img=nuevo_img+1                     
                                except IntegrityError as e:
                                    print('ERROR REF: '+p.ref)  
                                    print('ERROR SCR: '+image.find('src'))  
                                    error_img=error_img+1 
                                    pass             
                        else:
                            print(src+' NOT EXIST')
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
    externo.n_imagenes = len(Imagen.objects.all())
    externo.save() 
    return render(request, 'shop/externo_detail.html', {
        'externo': externo,
        'tamano': externo.file.size/1048576,
        'salida': [salida],
    }) 

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
                        parent = Null
                        for fab_name in fabricante_jerarquia.split('|'):
                            if fab_name:
                                name=fab_name
                            else:
                                name = 'DIABLA ROJA'
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
                    fab_name = 'DIABLA ROJA' 
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
    return render(request, 'shop/externo_detail.html',{
        'externo': externo,
        'tamano': externo.file.size/1048576,
        'salida': [salida],
    }) 

def templateshop(request):
    return render(request,"shop/templateshop.html")

def product_test(request):
    init_loaddata(request)
    return redirect('product_home')

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

def fabricante_home(request):
    fichas = Fabricante.objects.filter(parent=None)
    return render(request,"shop/fabricante_home.html",{
        'fichas': fichas,
    })

def fabricante_list(request):
    fichas = Fabricante.objects.filter(parent=None)
    return render(request,"shop/fabricante_list.html",{
        'fichas': fichas,
    })

def fabricante_home(request):
    fichas = Fabricante.objects.filter(parent=None)
    return render(request,"shop/fabricante_home.html",{
        'fichas': fichas,
    })

def fabricante_detail(request,slug):
    prod_page=int(Configuracion.objects.get(variable='prod_page').valor)
    fabricantes = Fabricante.objects.all().order_by('name')
    fabricante_slug = slug.split('/')
    fabricante_queryset = list(fabricantes)
    all_slugs = [ x.slug for x in fabricante_queryset ]
    parent = None
    for slug in fabricante_slug:
        if slug in all_slugs:
            parent = get_object_or_404(Fabricante,slug=slug,parent=parent)
    breadcrumbs_link = parent.get_fab_list('/')
    #breadcrumbs_link.append(slug)
    #print(breadcrumbs_link)
    fabricante_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link]
    breadcrumbs = zip(breadcrumbs_link, fabricante_name)
    sub_fabricantes = parent.children.all()
    #fichas = Imagen.objects.filter(preferred=True, product_id__fabricante_slug__in=breadcrumbs_link).order_by('-product_id__updated')
    #fichas_prod = Product.objects.filter(fabricante__in=sub_fabricantes)
    fichas_prod = Imagen.objects.filter(
        Q(preferred=True),
        Q(product_id__fabricante__in=sub_fabricantes)|Q(product_id__fabricante=parent)).order_by('-product_id__release_date','product_id__fabricante__name')
    paginator = Paginator(fichas_prod, prod_page)
    page = request.GET.get('page')
    fichas_prod_paginado = paginator.get_page(page)
    return render(request, "shop/fabricante_detail.html", {  
        'breadcrumbs': breadcrumbs,  
        'ficha': parent,
        'sub_fabricantes': sub_fabricantes, 
        'fichas_prod': fichas_prod_paginado,
        'n_prod': paginator.count
    })