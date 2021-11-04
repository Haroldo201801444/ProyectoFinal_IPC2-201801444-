const documento = document.getElementById('documento');
const input = document.getElementById('entrada');

documento.addEventListener('change', (e) => {
    const archivo = e.target.files[0];
    const lectura = new FileReader(); //FileReader() permite que las aplicaciones web lean ficheros (o información en buffer) almacenados en el cliente de forma asíncrona
    lectura.readAsText(archivo)

    lectura.addEventListener('load', (e) => {
        input.innerHTML = lectura.result
        valor = lectura.result
    });
});
/*el metodo readAsText() comienza la lectura del contenido del objeto File/Blob, una vez terminada, 
el atributo result contiene el contenido del fichero como una cadena de texto.*/