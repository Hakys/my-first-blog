from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.utils import timezone
from django.utils.text import slugify
from django.utils.dateparse import parse_datetime
from datetime import datetime
from time import time
from django.db import models, IntegrityError
from django.db.models import Q
import xml.etree.ElementTree as ET
from django.conf import settings
from django.core.files import File
from django.core.files.storage import Storage, FileSystemStorage
from urllib.request import Request, urlopen, URLError, HTTPError  
from django.core.exceptions import ObjectDoesNotExist
from django.http import *
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from decimal import *
from django.contrib.auth import *
from django.contrib.auth.decorators import login_required
from django.urls import reverse

def init_loadfile(request):
    salida=[]   #{'retorno': 0,'salida': "no error"}
    try:
        obj = Externo(name='DreamLove_Productos', url='https://store.dreamlove.es/dyndata/exportaciones/csvzip/catalog_1_50_8_0_f2f9102e37db89d71346b15cbc75e8ce_xml_plain.xml')
        obj.importar()
        obj.save()
    except IntegrityError as e:
        salida.append({'retorno': -1,'salida': e})
    try:
        obj = Externo(name='DreamLove_Marcas',url='https://store.dreamlove.es/UserFiles/Marcas__todos_.csv')
        obj.importar()
        obj.save()
    except IntegrityError as e:
        salida.append({'retorno': -1,'salida': e})
    try:
        obj = Externo(name='DreamLove_Categorias', url='https://store.dreamlove.es/dyndata/exportaciones/csvzip/categories_1_50_c5717766e188bb03da6d308655f4d8dd.csv')
        obj.importar()
        obj.save()
    except IntegrityError as e:
        salida.append({'retorno': -1,'salida': e})
    return externo_home(request,salida)

def index(request):
    # Call function to handle the cookies
    visitor_cookie_handler(request)

    return render(request,"shop/index.html", { 
        'visits': request.session['visits'],   
        'fabricantes' : Fabricante.objects.filter(parent=None),
    })

''' #####   CATEGORY   ##### '''

def category_home(request):
    fichas = Fabricante.objects.filter(parent=None)
    return render(request,"shop/category_home.html",{
        'fichas': fichas,
    })

''' #####   PRODUCTOS   ##### '''

def product_list(request):
    todo = Imagen.objects.filter(preferred=True).order_by('-product_id__release_date')    
    prod_page=int(Configuracion.objects.get(variable='prod_page').valor)
    #print(prod_page)
    paginator = Paginator(todo, prod_page)
    page = request.GET.get('page')
    todo_paginado = paginator.get_page(page)
    return render(request, 'shop/product_list.html', {'todo':todo_paginado})

def product_home(request, salida=[]):
    fichas_prod = Imagen.objects.filter(preferred=True,product_id__release_date__gte=datetime.today()).order_by('-product_id__release_date')
    return product_filtrados(request, 'Próximos Lanzamientos', fichas_prod, salida)

def product_lanzamientos(request, salida=[]):
    fichas_prod = Imagen.objects.filter(preferred=True,product_id__release_date__gt=datetime.today()).order_by('-product_id__release_date')
    return product_filtrados(request, 'Próximos Lanzamientos', fichas_prod, salida)

def product_nuevos(request, salida=[]):
    fichas_prod = Imagen.objects.filter(preferred=True,product_id__new=True).order_by('-product_id__release_date')
    return product_filtrados(request, 'Novedades', fichas_prod, salida)

def product_rebajados(request, salida=[]):
    fichas_prod = Imagen.objects.filter(preferred=True,product_id__sale=True).order_by('-product_id__updated')    
    return product_filtrados(request, 'Rebajados', fichas_prod, salida)

def product_descatalogados(request, salida=[]):
    fichas_prod = Imagen.objects.filter(preferred=True,product_id__destocking=True).order_by('-product_id__updated')    
    return product_filtrados(request, 'Descatalogados', fichas_prod, salida) 

def product_filtrados(request, title, fichas_prod, salida=[]):   
    prod_page=Configuracion.objects.get(variable='prod_page').get_valor_int()
    paginator = Paginator(fichas_prod, prod_page)
    page = request.GET.get('page')
    fichas_prod_paginado = paginator.get_page(page)
    return render(request, 'shop/product_cat.html',{
        'title': title,
        'fichas_prod': fichas_prod_paginado,
        'salida': salida,
    })

def product_detail(request, pk, salida=[]):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        #raise Http404("Product does not exist")
        salida.append({
            'retorno': -1,
            'salida': "Producto No Encontrado"
            })
        return product_home(request, salida)
    images = Imagen.objects.filter(product_id__pk=product.pk).order_by('-preferred')
    breadcrumbs_link = product.get_fab_list('/')
    fabricante_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link]
    breadcrumbs = zip(breadcrumbs_link, fabricante_name)
    #pvp=product.get_pvp()
    
    iva=Decimal(product.vat/100)
    beneficio = Configuracion.objects.get(variable='beneficio').get_valor_dec()
    rec_equivalencia = Configuracion.objects.get(variable='rec_equivalencia').get_valor_dec()
    
    req=Decimal(rec_equivalencia/1000)
    porc_benef=Decimal(beneficio/100)
    coste_total=product.cost_price+(product.cost_price*iva)+(product.cost_price*req)
    #'pvp':  coste_total/(1-porc_benef),
    #'price_iva': product.price*(1+iva),
    #'recommended_retail_price_iva': product.recommended_retail_price*(1+iva),
    #'default_shipping_cost_iva': product.default_shipping_cost,
    return render(request, 'shop/product_detail.html', {
        'porc_benef': porc_benef,
        'beneficio': (coste_total/(1-porc_benef))-coste_total,
        'hoy': datetime.today(),
        'date_min': datetime.min,
        'product': product, 
        'images':images, 
        'breadcrumbs':breadcrumbs,
        'salida':salida,
    })

def product_detail_slug(request, slug, salida=[]):    
    try:
        product = Product.objects.get(Q(ref=slug)|Q(slug=slug))
    except Product.DoesNotExist:
        #raise Http404("Product does not exist")
        salida.append({
            'retorno': -1,
            'salida': "Producto No Encontrado"
            })
        return product_home(request, salida)
    return product_detail(request, product.pk, salida)

def product_anadir(request, slug):
    salida=[]
    if not slug:
        salida.append({
            'retorno': -1,
            'salida': " Solicitud no Encontrado ",
            })
        return product_home(request, salida)
    externo = get_object_or_404(Externo, name='DreamLove_Productos')
    tree=ET.parse(externo.path())
    root=tree.getroot()
    lista=[slug]
    for prod in root.findall('product'):
        ref = prod.find('public_id').text
        if not ref in lista:
            root.remove(prod)
        #else:
            #ET.dump(prod)
    
    if not root:
        salida.append({
            'retorno': -1,
            'salida': " Producto no Encontrado ",
            })
        return product_home(request, salida)
    else:
        salida.append(procesar_productos(root,True))
        salida.append(procesar_fabricantes(root))  
        salida.append(procesar_imagenes(root))
    print(salida)
    return product_detail_slug(request, slug, salida)

def product_actualizar(request, slug):
    externo = get_object_or_404(Externo, name='DreamLove_Productos')
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
    if not root:
        #print('Producto Borrado')
        salida.append(product_borrar(request,slug))
    else:
        salida.append(procesar_productos(root,True))
        salida.append(procesar_fabricantes(root))  
        salida.append(procesar_imagenes(root))
    return product_detail_slug(request, slug, salida)

def product_borrar(request, slug):
    externo = get_object_or_404(Externo, name='DreamLove_Productos')
    tree=ET.parse(externo.path())
    root=tree.getroot()
    n, resultado = Product.objects.filter(Q(ref=slug)|Q(slug=slug)).delete()
    #n = Product.objects.filter(Q(ref=slug)|Q(slug=slug)).count
    salida=[{
        'retorno': n,
        'salida': " borrado/s "+str(resultado)
        }]
    return product_home(request, salida)

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

''' #####   EXTERNO   ##### '''

def externo_home(request, salida=[]):
    todo = Externo.objects.all().order_by('-updated_date')
    #if todo.count()==1:
    #    return externo_detail(request, todo[0].pk)
    #else:
    return render(request, 'shop/externo_home.html', {
        'todo':todo,
        'salida': salida,
        })

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
            ext = Externo.objects.get(name='DreamLove_Productos')
        except ObjectDoesNotExist as e:
            init_loadfile(request)
            ext = get_object_or_404(Externo, name='DreamLove_Productos')
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

def procesar_productos(root,insertar=False):
    if root:
        limite=int(get_object_or_404(Configuracion, variable='product_limite').valor)
        iva_21 = Configuracion.objects.get(variable='iva').get_valor_dec()
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
                if p.updated < updated or insertar:
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
                        p.product_url = prod.find('product_url').text 
    
                        p.vat = Decimal(prod.find('vat').text)
                        iva=1+(p.vat/100)
                        p.cost_price = Decimal(prod.find('cost_price').text)
                        p.pvp=p.get_pvp()
                        aux = Decimal(prod.find('price').text)
                        p.price = aux*iva
                        aux = Decimal(prod.find('recommended_retail_price').text)
                        p.recommended_retail_price = aux*iva                       
                        aux = Decimal(prod.find('default_shipping_cost').text)
                        p.default_shipping_cost = Decimal(aux*(1+iva_21/100)).quantize(Decimal('.01'), rounding=ROUND_UP)+Decimal(0.50)
                        #if p.default_shipping_cost < 5.5:
                        #    p.default_shipping_cost = 5.5

                        p.updated = updated                    
                        p.html_description = prod.find('html_description').text
                        p.delivery_desc = prod.find('delivery_desc').text
                        
                        if prod.find('unit_of_measurement').text=='units':
                            p.unit_of_measurement = 'unidad/es'
                        else:
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
        limite=int(Configuracion.objects.get(variable='fabricante_limite').valor)
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

''' #####   VARIOS   ##### '''

def templateshop(request):
    return render(request,"shop/templateshop.html")

def about(request):
    request.session.set_test_cookie()
    #init_loaddata(request)
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    return HttpResponseRedirect(reverse('index'))

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

''' #####   FABRICANTE   ##### '''

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
        'hoy': datetime.today(), 
        'breadcrumbs': breadcrumbs,  
        'ficha': parent,
        'sub_fabricantes': sub_fabricantes, 
        'fichas_prod': fichas_prod_paginado,
    })

''' #####   USERPROFILE   ##### '''

def some_view(request):
    if not request.user.is_authenticated():
        return HttpResponse("You are logged in.")
    else:
        return HttpResponse("You are not logged in.")

@login_required
def user_restricted(request):
    return HttpResponse("Since you're logged in, you can see this text!")

@login_required
def user_myprofile(request):
    return HttpResponse("Datos de Mi Perfil!")


''' #####   COOKIES   ##### '''

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,
        'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    
    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        #update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # set the last visit cookie
        request.session['last_visit'] = last_visit_cookie
    
    # Update/set the visits cookie
    request.session['visits'] = visits

''' #####   #####   ##### '''