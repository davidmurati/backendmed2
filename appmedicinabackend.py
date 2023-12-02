from flask import Flask, jsonify, render_template, request
from flask_pymongo import PyMongo
from flask_cors import CORS

from bson import ObjectId

#------------------------------------------------

from selenium import webdriver
import time

from selenium import webdriver
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

#--------------------------------------------

import re
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as ec


#-----------------------------------------------

app = Flask (__name__)
app.config['MONGO_URI']='mongodb://localhost/Med2Scrapydb'
mongo = PyMongo(app)

db = mongo.db.resultado


# Settings
CORS(app)


# Routes
@app.route('/resultado', methods=['POST'])
def run_automation():
    if request.method == 'POST':
         # search_key es lo capturado por el textbox
        data = request.get_json()

        if 'consulta' in data:  # Assuming 'consulta' is the key for captured text
            search_key = data['consulta'] 

        
        title = obtener_resultado(search_key)

        id = db.insert_one({
        'Respuesta': title,
        
    })
        
    return jsonify({'id': str(id.inserted_id), 'msg': 'User Added Successfully!'})

    

@app.route('/resultado', methods=['GET'])
def getUsers():
    users = []
    for doc in db.find():
        users.append({
            '_id': str(ObjectId(doc['_id'])),
            'Respuesta': doc['Respuesta']
        })
    return jsonify(users)


#---------------Borra respuesta generada todo

@app.route('/resultado', methods=['DELETE'])

def deleteUser2():
  db.delete_many({})
  return jsonify({'message': 'User Deleted'})

#---------------Borra respuesta generada


@app.route('/resultado/<id>', methods=['DELETE'])
def deleteUser(id):
  db.delete_one({'_id': ObjectId(id)})
  return jsonify({'message': 'User Deleted'})

#----------------------------------------


@app.route('/')
def index():
    return '<h1> index.html </h1>'


#-------------para que se corra en segundo plano

chrome_options = Options() 
#chrome_options.add_argument("--headless")



def obtener_resultado( search_key):

    try:

        # Inicializa el navegador Chrome utilizando Selenium
        S = Service (ChromeDriverManager().install())
        driver = webdriver.Chrome (options= chrome_options, service=S)
        driver.maximize_window()
        
    
        #----------------------------------------------

        search_key = search_key
        
        # Abre la página deseada (en este ejemplo, abrirá Google)

        driver.get('https://doctorgpt.live/')

        # tiempo de espera para poder ejecutar 
        time.sleep(3)


        # Encuentra el campo de búsqueda y envía la consulta

        #driver.find_element(By.NAME, 'email').send_keys('davidmgil26790@gmail.com')
        #driver.find_element(By.NAME, 'password').send_keys('20154372.mg')
        
        #-------------espera a que l elemento sea cliqueable
        #WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.CLASS_NAME, 'MuiButtonBase-root.css-1cjg38l')))
        #time.sleep(3)

        #driver.find_element(By.CLASS_NAME, 'MuiButtonBase-root.css-1cjg38l').submit()


        #----------------------------Generar diagnostico

        #time.sleep(2)

        driver.find_element(By.ID, 'issue').send_keys(search_key)
    
        time.sleep(3)

        driver.find_element(By.CLASS_NAME, 'btn.btn-primary').click()

        time.sleep(3)

        #----------------------paso extra 

        WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.CLASS_NAME, 'btn.btn-primary.btn-lg')))

        driver.find_element(By.CLASS_NAME, 'btn.btn-primary.btn-lg').click()

        #--------------------Extraer la GENERACIÓN DE LA RESPUESTA

        time.sleep(3)

        # inicializamos el string de la respuesta
        respuesta = ""
        #timestamp de inicio de la generación de la respuesta
        
        while True:
            # extraemos el texto generado
            e= driver.find_elements (By.ID, "diagnosis-body")[-1]
            respuesta = e.text
            try:
                #elemento de los 3 puntitos animados mientras se genera la respuesta
                if driver.find_element(By.CLASS_NAME, "MuiButtonBase-root.css-19abu36").is_enabled==False:
                    david=True
                else:
                    david=False
                    break
                # si el elemento existe es porque se ha empezado a generar la respuesta
            except: #st el elemento ya no existe
                #st los 3 puntitos ya no están, es que la respuesta ha terminado
                
                if respuesta: # st se ha generado alguna respuesta
                    break

        e= driver.find_elements (By.ID, "diagnosis-body")[-1]
        respuesta = e.text
        
        
        time.sleep(5)
        
        #-------------------------Truncar salida hasta la opcion Tips.

        if respuesta.find("Treatment")!=-1:
            contador= respuesta.find("Treatment")
        else:
            contador= len(respuesta)-1

        contador2= 0
        
        startLoc = contador2
        endLoc = contador
        respuesta = respuesta[startLoc: endLoc]


        #------------------------conexion con ia

        driver.get('https://labs.perplexity.ai/')

        #time.sleep(3)


        #---------------------------------------

        #-------------espera a que l elemento sea cliqueable
        WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.ID, 'lamma-select')))

        #-------------------------------select

        select_element = driver.find_element(By.ID, 'lamma-select')
        select = Select(select_element)

        #time.sleep(3)
        
        select.select_by_visible_text('codellama-34b-instruct')
        

        #---------------------------------------

        #--------------------------Enviar informacion y consultar

        respuesta2=""
        respuesta=respuesta

        time.sleep(3)

        driver.find_element(By.TAG_NAME, "textarea").send_keys("Instruccion: resume en español el texto: ")
        time.sleep(2)


        WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.ID, 'lamma-select')))

        time.sleep(3)

        driver.find_element(By.TAG_NAME, "textarea").send_keys(respuesta)
        time.sleep(5)

        driver.find_element(By.TAG_NAME, "textarea").send_keys(Keys.ENTER)

    #-------------espera a que l elemento sea cliqueable
        WebDriverWait(driver, 30).until(ec.element_to_be_clickable((By.ID, 'lamma-select')))
        
        time.sleep(7)

        #--------------------------------captura de todo el html de la pagina


        html = driver.page_source
        time.sleep(4)
        respuesta2=html

        #-------------------------------Extraer del html la respuesta generada de la ia

        i=0
        while True:       
            if respuesta2.find("word-break:break-word")!=-1:

                # el +3 es para que pueda buscar la palabra siguiente sin quedarse estancado en la misma
                inicio= respuesta2.index("word-break:break-word")+3
                respuesta2=respuesta2[inicio: len(respuesta2)-1]    
                i=i+1
            
            if i==10:
                break

        if respuesta2.find("flex items-start ml-sm mt-xs gap-x-xs max-w-full")!=-1:
            fin= respuesta2.find("flex items-start ml-sm mt-xs gap-x-xs max-w-full")
        else:
            fin= len(respuesta2)-1


        #-------------------------------Extraccion de la respuesta del html

        startLoc = 0
        endLoc = fin
        respuesta2 = respuesta2[startLoc: endLoc]

        #-------------------------------

        #-------------------------------Extraer de las etiquetas la respuesta

        etiqueta_inicio = '<span class="">'
        etiqueta_fin = '</span>'

        resultados = re.findall(rf'{etiqueta_inicio}(.*?){etiqueta_fin}', respuesta2)
        respuesta2 = ' '.join(resultados)

    #-------------------------------

        # Cierra el navegador
        driver.quit()

    except:

        respuesta2= ("Ha ocurrido un error, no se genero la respuesta. Vuelva a intentarlo")

    return respuesta2


if __name__ == '__main__':
    app.run(debug=True)