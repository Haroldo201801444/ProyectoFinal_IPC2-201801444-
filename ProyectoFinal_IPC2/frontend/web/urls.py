from django.urls import path
from web import views  #importamos el archivo views del paquete web

urlpatterns = [
    path('home',views.home,name="Home"),
    path('reportes',views.reportes,name="Reportes"),
]