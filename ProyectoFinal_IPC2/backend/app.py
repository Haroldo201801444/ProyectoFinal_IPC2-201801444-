from flask import Flask,Response, request                  #importar el framework flask
from flask_cors import CORS
from admin import Administrador

app = Flask(__name__)                       #creamos una aplicacion flask, para ello instanceamos el objeto flask

cors = CORS(app,resources={r"/*":{'origin':'*'}}) #habilita que se pueda acceder a la api hecha en flask desde direcciones ip externas o desde otros programas(fronted)

admin = Administrador() #instancea para acceder a todos los metodos de la clase Administrador para manipular la informacion

@app.route('/procesar',methods=['POST'])
def procesar():
    envio_datos = request.data.decode('utf-8')   #capturamos los datos enviados desde postman/django con la request POST
    print("-----------------------------------------------------")
    
    admin.analisis_archivo(admin.lecturaXML(envio_datos))             #enviamos el archivo xml a la clase Administrador que se encargara de capturar la informacion del archivo xml
    
    return "<h1>El archivo fue enviado correctamente al servidor Flask</h1>"

@app.route('/consultadatos',methods=['GET'])
def procesardatos():
    valores = admin.archivo_salida_XML()  #variable que contendra el archivo de xml de salida devuelto por este metodo

    return Response(status=200,response=valores)  #aqui lo regresemos a postman/frontend django

@app.route('/resumen_por_fecha',methods=['GET'])
def resumen_por_fecha():
    fecha = request.args.get('fecha')
    
    admin.generarGraficaporFecha(fecha)

    return Response(status=200,response="<h1>Se genero correctamente la grafica de barras</h1>")

@app.route('/resumen_rango_fecha',methods=['GET'])
def resumen_rango_fecha():
    fechaUno = request.args.get('fechaUno')
    fechaDos = request.args.get('fechaDos')
    eleccion = request.args.get('eleccion')

    admin.generarRangoFecha(fechaUno,fechaDos,eleccion)

    return Response(status=200,response="<h1>Se genero correctamente la grafica de barras</h1>")

def pagina_no_encontrada(error):
    return "<h1>La pagina que intentas buscar no existe</h1>"

def peticion_no_permitida(error):
    return "<h1>La peticion http no está permitido para la URL solicitada</h1>"

if __name__ == '__main__':                  
    app.register_error_handler(404,pagina_no_encontrada)    #se ejecutara cuando la página que se ha intentado buscar no existe en el servidor
    app.register_error_handler(405,peticion_no_permitida)                                                        #indica que el cliente usa un método HTTP no permitido
    
    app.run(debug=True,port=4000)                           #indicamos que estamos en modo de prueba y que el servidor Flask va a correr en el puerto 4000

