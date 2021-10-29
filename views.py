#en este archivo vamos a crear todas las vistas a utilizar en nuestro frontend(DJANGO)
from django.shortcuts import render

def home(request):
    return render(request,'web/index.html')

def reportes(request):
    return render(request,'web/reporte.html')