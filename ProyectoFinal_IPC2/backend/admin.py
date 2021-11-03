import xml.etree.ElementTree as ET  #importamos este modulo para leer y escrbir archivos xml
import re                           #importamos este modulo regex para trabajar con expresiones regulares
import random                       #importamos el paquete para generar el codigo aleatorio de cada factura aprobada
import matplotlib.pyplot as plt     #Matplotlib es una librería de Python especializada en la creación de gráficos en dos dimensiones
from PaPDF import PaPDF             #paquete para generar archivos pdf

from operator import itemgetter
from itertools import groupby

class Administrador:
    def __init__(self):
        self._archivo_salida_xml = ""
        self._archivo_analizar_graficas = ""

    def lecturaXML(self,archivo_entrada):
        archivo = open("C:/Users/Haroldo Donis/Desktop/servidor.xml","w+")
        archivo.write(archivo_entrada)

        lectura = open("C:/Users/Haroldo Donis/Desktop/servidor.xml","r")
        
        diccionario = []
        raiz = ET.parse(lectura) #parseamos el archivo xml a una variable llamada raiz
        valor = raiz.getroot()          #capturamos el nodo principal del arbol

        for i in valor.findall('DTE'):  #accedemos a cada conjuntos de etiquetas dentro de la etiqueta DTE
            temporal = {}
            valor_factura = []
            for j in i:                 #recorremos una a una las etiquetas que contiene la etiqueta DTE
                try:
                    if j.tag == "TIEMPO":
                        patron = r'(\d{2})/(\d{2})/(\d{4})'  #creamos una expresion regular para capturar las fechas solamente
                        fecha = re.findall(patron,j.text)   #hara una busqueda segun el patron indicado en la variable indicada, devuelve un arreglo con todas las condiciones como una lista

                        if not fecha:  #verificamos si la lista esta vacia
                            temporal.update({j.tag: "fecha incorrecta"})

                        fecha_correcta = f"{fecha[0][2]}-{fecha[0][1]}-{fecha[0][0]}"
                        temporal.update({j.tag: fecha_correcta})

                    elif j.tag == "NIT_RECEPTOR" or j.tag == "NIT_EMISOR":
                        lista = list(j.text)  #eliminamos cualquier espacio en blanco dentro del nit
                        listaNumeros = [2,3,4,5,6,7,2,3,4,5,6,7,2,3,4,5,6,7]
                        for i in lista:        #eliminamos todos los espacios en blanco que puedan venir
                            if i == " ":
                                lista.remove(i) #Eliminar un elemento por su valor

                        ubicacion = lista[-1]  #agarramos el ultimo valor del nit para poder verificarlo
                        lista.pop(-1)           #Eliminar un elemento por su indice
                        reverso = list(reversed(lista))  #voltemos la lista al reves para aplicar el algoritmo del modulo 11

                        for i in range(len(reverso)):
                            reverso[i] = int(reverso[i])  #convertimos nuestra lista str en una lista int para poder hacer operaciones matematicas

                        sumaValores = []   #lista que contendra la sumatoria final para luego calcular el modulo 11 a esta sumatoria
                        for (a,b) in zip(reverso,listaNumeros):
                            if a is not None:
                                sumaValores.append(a*b)
                        primer_modulo = 11 - (sum(sumaValores)%11) #obtenemos el primer modulo 11
                        if primer_modulo<10 and str(primer_modulo) == ubicacion:
                            condicion = "correcto"  # variable que contendra si el nit es correcto o no correcto

                        elif primer_modulo==10 and ubicacion == 'K':
                            condicion = "correcto"  # variable que contendra si el nit es correcto o no correcto

                        elif primer_modulo==11 and int(ubicacion) == 0:
                            condicion = "correcto"  # variable que contendra si el nit es correcto o no correcto

                        else:
                            condicion = "incorrecto"  # variable que contendra si el nit es correcto o no correcto

                        temporal.update({j.tag:{"valor" : j.text,"condicion" : condicion}})

                    elif j.tag == 'VALOR':
                        valor_factura.append(float(j.text))
                        temporal.update({j.tag: float(j.text)})

                    elif j.tag == 'IVA':
                        valor_factura.append(float(j.text))
                        temporal.update({j.tag: float(j.text)})

                    elif j.tag == "TOTAL":
                        total = valor_factura[0] + valor_factura[1] #verificamos si el iva esta bien calculado

                        if total == float(j.text):
                            condicion = "correcto"
                        else:
                            condicion = "incorrecto"

                        temporal.update({j.tag: {"valor": j.text, "condicion": condicion}})
                    else:
                        temporal.update({j.tag: j.text})
                except:
                    pass
            diccionario.append(temporal)

        return diccionario  #retorna una lista que contendra toda la informacion de cada movimiento por fecha en diccionarios de python
#-------------------------------verificamos si se introdujo la informacion de forma correcta-------------------------------
    def analisis_archivo(self,diccionario):
        lista = diccionario
        lista.sort(key=itemgetter('TIEMPO')) #ordenamos nuestros diccionarios por la clave TIEMPO que estan en la lista llamada lista

        lista_fecha_agrupada = []
        print("Despliegue de facturas por fecha : ")
        for fecha,elementos in groupby(lista,key=itemgetter('TIEMPO')):
            temporal = []
            print(fecha)
            for elemento in elementos:
                print("     ",elemento)
                temporal.append(elemento)
            lista_fecha_agrupada.append(temporal)

        self.escrituraXML(lista_fecha_agrupada)

        self._archivo_analizar_graficas = lista_fecha_agrupada

    def escrituraXML(self,archivo_analisado):
        autorizaciones = ET.Element("LISTA_AUTORIZACIONES")  # escribimos el nodo raiz de nuestro archivo XML

        for i in archivo_analisado:          
            autorizacion = ET.SubElement(autorizaciones,"AUTORIZACION")
            ET.SubElement(autorizacion, "FECHA").text = i[0]["TIEMPO"]

            facturas_recibidas = 0
            for j in i:
                facturas_recibidas = facturas_recibidas + 1
            ET.SubElement(autorizacion,"FACTURAS_RECIBIDAS").text = str(facturas_recibidas)

            errores = ET.SubElement(autorizacion, "ERRORES")
            emisor_incorrecto = 0 ; receptor_incorrecto = 0 ; total_iva_incorrecto = 0
            emisor_correcto = 0 ; receptor_correcto = 0

            referencia = [] ; nueva = []
            for j in i:
                referencia.append(j["REFERENCIA"])
            conjunto = list(set(referencia))       #en esta lista guardamos las referencias unicas,quitamos las duplicadas
            total = len(referencia)-len(conjunto)  #variable que guarda la cantidad de referencias duplicadas

            for j in i:  #vamos verificando y contando todos los errores encontrados en los nit y la suma del total del iva
                if j["NIT_EMISOR"]["condicion"] == "incorrecto":
                    emisor_incorrecto = emisor_incorrecto + 1
                else:
                    emisor_correcto = emisor_correcto + 1

                if j["NIT_RECEPTOR"]["condicion"]== "incorrecto":
                    receptor_incorrecto = receptor_incorrecto + 1
                else:
                    receptor_correcto = receptor_correcto + 1

                if j["TOTAL"]["condicion"] == "incorrecto":
                    total_iva_incorrecto = total_iva_incorrecto + 1

            ET.SubElement(errores, "NIT_EMISOR").text = str(emisor_incorrecto)
            ET.SubElement(errores, "NIT_RECEPTOR").text = str(receptor_incorrecto)
            ET.SubElement(errores, "TOTAL_IVA").text = str(total_iva_incorrecto)
            ET.SubElement(errores, "REFERENCIAS_DUPLICADAS").text = str(total)

            ET.SubElement(autorizacion, "FACTURAS_CORRECTAS").text = str("facturas correctas")
            ET.SubElement(autorizacion, "CANTIDAD_EMISORES").text = str(emisor_correcto)
            ET.SubElement(autorizacion, "CANTIDAD_RECEPTORES").text = str(receptor_correcto)

            listado_autorizaciones = ET.SubElement(autorizacion,"LISTADO_AUTORIZACIONES")
            for j in i:
                if j["NIT_EMISOR"]["condicion"] == "correcto":
                    aprobacion = ET.SubElement(listado_autorizaciones, "APROBACION")
                    comienza = random.randint(1021090100000001, 9021090100000001)
                    ET.SubElement(aprobacion, "NIT_EMISOR", ref=j["REFERENCIA"]).text = j["NIT_EMISOR"]["valor"]
                    ET.SubElement(aprobacion, "CODIGO_APROBACION").text = str(comienza)

        ruta = "C:/Users/Haroldo Donis/Desktop/salida.xml"
        archivo = ET.ElementTree(autorizaciones)  # convierte nuestro arbol en un archivo xml
        
        archivo.write(ruta)  # guardamos nuestro archivo dentro de nuestro directorio en la ruta indicada

        self._archivo_salida_xml = open(ruta,"r") 

    def archivo_salida_XML(self):  #en este metodo retornamos el valor del archivo de salida xml
        return self._archivo_salida_xml

    def generarGraficaporFecha(self,entrada):

        archivo_analisado = self._archivo_analizar_graficas 

        for i in archivo_analisado:
            lista = []
            for j in i:
                if j['TIEMPO'] == entrada:  #verificamos si la fecha ingresada existe en nuestra base de datos
                    if j['NIT_EMISOR']['condicion'] == "correcto":
                        lista.append(j['NIT_EMISOR']['valor'])
                    if j['NIT_RECEPTOR']['condicion'] == "correcto":
                        lista.append(j['NIT_RECEPTOR']['valor'])
            
            if len(lista) != 0:
                frecuencia = {}  #en esta lista se guardara la frecuencia de todos los nits ingresados en la fecha indicada
                for n in lista:
                    if n in frecuencia:
                        frecuencia[n] = frecuencia[n] + 1
                    else:
                        frecuencia[n] = 1

                listaUno = list(frecuencia.keys())
                listaDos = list(frecuencia.values())

                fig, ax = plt.subplots()
                # Creamos la grafica de barras
                plt.bar(listaUno,listaDos)
                plt.savefig('C:/Users/Haroldo Donis/Desktop/ProyectoFinal_IPC2/frontend/web/static/web/img/imagenUno.png')

    def generarRangoFecha(self,entradaUno,entradaDos,opcion):
        
        archivo_analisado = self._archivo_analizar_graficas 

        listaFechas = [] ; listaValores_Sin_IVA = [] ; listaValores_Totales = []
        for i in archivo_analisado:
            valor_Total = 0 ; valor_Sin_IVA = 0 ; fecha = ""
            for j in i:
                if entradaUno <= j["TIEMPO"] and entradaDos >= j["TIEMPO"]:
                    fecha = j["TIEMPO"]
                    valor_Sin_IVA = valor_Sin_IVA + j["VALOR"]
                    valor_Total = valor_Total + float(j["TOTAL"]["valor"])

            if valor_Total != 0 and valor_Sin_IVA != 0 and fecha != "":
                listaFechas.append(fecha)
                listaValores_Sin_IVA.append(valor_Sin_IVA)
                listaValores_Totales.append(valor_Total)

        if opcion == '1': #grafica con los valores totales
            listaUno = listaFechas
            listaDos = listaValores_Totales

            fig, ax = plt.subplots()
            # Creamos la grafica de barras
            plt.bar(listaUno, listaDos)
            plt.savefig('C:/Users/Haroldo Donis/Desktop/ProyectoFinal_IPC2/frontend/web/static/web/img/imagenDos.png')

        if opcion == '0': #grafica con los valores sin IVA
            listaUno = listaFechas
            listaDos = listaValores_Sin_IVA

            fig, ax = plt.subplots()
            # Creamos la grafica de barras
            plt.bar(listaUno, listaDos)
            plt.savefig('C:/Users/Haroldo Donis/Desktop/ProyectoFinal_IPC2/frontend/web/static/web/img/imagenDos.png')

    def generar_archivo_pdf(self):
        try:
            with PaPDF("C:/Users/Haroldo Donis/Desktop/ProyectoFinal_IPC2/frontend/web/static/web/archivo.pdf") as pdf:
                pdf.addText(30, 130,"RESUMEN DE LOS MOVIMIENTOS DE NITS POR FECHA ")
                pdf.addImage("C:/Users/Haroldo Donis/Desktop/ProyectoFinal_IPC2/frontend/web/static/web/img/imagenUno.png",50,20,100,100)

                pdf.addText(30, 270, "RESUMEN POR RANGO DE FECHA")
                pdf.addImage("C:/Users/Haroldo Donis/Desktop/ProyectoFinal_IPC2/frontend/web/static/web/img/imagenDos.png", 50, 160, 100, 100)
        except:
            pass
        