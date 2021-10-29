from django.urls import path
from web import views

urlpatterns = [ #en esta parte comenzamos a crear nuestras urls
    path('home',views.home,name='Home'),
    path('reportes',views.reportes,name='Reportes')
]
