from django.shortcuts import render,redirect
import requests
#aqui es donde creamos nuestras vistas de django
#Una View es un lugar donde ponemos la "lógica" de nuestra aplicación. 

endpoint = "http://localhost:4000{}"  #indicamos la ruta donde esta corriendo el servidor Flask 

def home(request):
    if request.method == 'GET': #todas las rutas al iniciarse invocan el metodo get, verifica si la pagina se recargo
        url = endpoint.format('/consultadatos')
        dato_capturado = requests.get(url)
        
        contenido = {
            'output' : dato_capturado.text,
        }

        return render(request,'web/home.html',contenido)  #reenderiazamos nuestras plantillas(templates) de django sin implementar ningun metodo de request

    elif request.method == 'POST':
        documento = request.FILES['documento']
        data = documento.read()     #leemos el archivo de texto enviado desde el formulario POST como un archivo de tipo bytes
        url = endpoint.format('/procesar')
        requests.post(url,data)

        return render(request,'web/home.html')    #redireccionamos la vista de la url con el nombre que le dimos -> path('home',views.archivos,name="Home")

def reportes(request):
     if request.method == 'GET': #todas las rutas al iniciarse invocan el metodo get, verifica si la pagina se recargo
        fecha = request.GET.get('date',None)
        fechaUno = request.GET.get('date1',None)
        fechaDos = request.GET.get('date2',None)
        eleccion = request.GET.get('eleccion',0)

        if fecha is not None:
            urlUno = endpoint.format('/resumen_por_fecha')
            requests.get(urlUno,{'fecha' : fecha})

        if fechaUno is not None:
            urlDos = endpoint.format('/resumen_rango_fecha')
            requests.get(urlDos,{"fechaUno":fechaUno,"fechaDos":fechaDos,"eleccion":eleccion})

        return render(request,'web/reportes.html')  #reenderiazamos nuestras plantillas(templates) de django sin implementar ningun metodo de request

    
    
    

