# CriptoAPI
Automatización de un proceso de extracción de datos de criptomonedas por medio de un API. Extrayendo información relevante como el precio, el volumen, y las distintas variaciones del precio que han sufrido las diez criptomonedas más comercializadas durante diferentes periodos, para la generación de gráficos comparativos y de comportamiento de precios en un lapso dado.


## Definición de API

An application programming interface (API) is a connection between computers or between computer programs. It is a type of software interface, offering a service to other pieces of software. A document or standard that describes how to build or use such a connection or interface is called an API specification. A computer system that meets this standard is said to implement or expose an API. The term API may refer either to the specification or to the implementation.

In contrast to a user interface, which connects a computer to a person, an application programming interface connects computers or pieces of software to each other. It is not intended to be used directly by a person (the end user) other than a computer programmer who is incorporating it into the software. An API is often made up of different parts which act as tools or services that are available to the programmer. A program or a programmer that uses one of these parts is said to call that portion of the API. The calls that make up the API are also known as subroutines, methods, requests, or endpoints. An API specification defines these calls, meaning that it explains how to use or implement them.

One purpose of APIs is to hide the internal details of how a system works, exposing only those parts a programmer will find useful and keeping them consistent even if the internal details later change. An API may be custom-built for a particular pair of systems, or it may be a shared standard allowing interoperability among many systems.

The term API is often used to refer to web APIs, which allow communication between computers that are joined by the internet. There are also APIs for programming languages, software libraries, computer operating systems, and computer hardware. APIs originated in the 1940s, though the term did not emerge until the 1960s and 1970s. Recent developments in utilizing APIs have led to the rise in popularity of microservices, which are ultimately loosely coupled services accessed through public APIs.

![image](https://user-images.githubusercontent.com/32172901/174460067-fc2001e4-4cd2-4926-9b96-b47858c30d35.png)

![image](https://user-images.githubusercontent.com/32172901/174460063-5dcfce0e-5d6a-4615-80c7-6cacc1989bac.png)


## API a utilizar

Utilizaremos una API que ha sido creada por parte de [coinmarketcap](https://coinmarketcap.com/), una web que se especializa en el seguimiento de información bursátil de criptomonedas.

![image](https://user-images.githubusercontent.com/32172901/174460106-adca876b-9c5f-449b-aec3-65b4b49c2da0.png)

![image](https://user-images.githubusercontent.com/32172901/174460113-115a3ee0-1feb-45ad-92cd-bf817d346ec1.png)

![image](https://user-images.githubusercontent.com/32172901/174460116-591d0a52-4a9b-4b78-9a5d-92091c2c58a9.png)


## Consulta a la API

    # Conexión al ambiente en producción con la llave dada.

    from requests import Request, Session
    from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
    import json

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
      'start':'1',
      'limit':'10',
      'convert':'USD'
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': '6045746f-8c7b-41bd-9e9e-e809b0e892fe',
    }

    session = Session()
    session.headers.update(headers)

    try:
      response = session.get(url, params=parameters)
      data = json.loads(response.text)
      print(data)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
      print(e)

Normalización de los datos, debido a que son almacenados en un directorio por la estructura Json

    import pandas as pd
    df=pd.json_normalize(data['data'])
    
![image](https://user-images.githubusercontent.com/32172901/174460249-626afc2d-ac08-40c5-96c4-ae42bd272c32.png)

    
Ingresar al df la fecha y hora de la consulta al API, se añade la conversión a la timezone  de Bogotá, Colombia.

    df['Timestamp']=pd.to_datetime('now').tz_localize('UTC').tz_convert('America/Bogota')

Creación de una función que se encargue de consultar el API y añadir la nueva información al df

    def api_runner():

        global df
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        parameters = {
          'start':'1',
          'limit':'10',
          'convert':'USD'
        }
        headers = {
          'Accepts': 'application/json',
          'X-CMC_PRO_API_KEY': '6045746f-8c7b-41bd-9e9e-e809b0e892fe',
        }

        session = Session()
        session.headers.update(headers)

        try:
          response = session.get(url, params=parameters)
          data = json.loads(response.text)
          print(data)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
          print(e)

        # LLevar los datos consultados y normalizados a un df

        import pandas as pd
        df=pd.json_normalize(data['data'])

        # Ingresar al df2 la fecha y hora de la consulta al API, se añade la conversión a la timezone  de Bogotá, Colombia.

        df['Timestamp']=pd.to_datetime('now').tz_localize('UTC').tz_convert('America/Bogota')

        df

        if not os.path.isfile(r'E:\Estudio\Análisis de datos\Proyectos\Crypto API\Cripto.csv'):
            df.to_csv(r'E:\Estudio\Análisis de datos\Proyectos\Crypto API\Cripto.csv', header = 'column_names')
        else:
            df.to_csv(r'E:\Estudio\Análisis de datos\Proyectos\Crypto API\Cripto.csv', mode ='a',header = False)
            
Creación de el loop para que la función se ejecute una cantidad de veces dada y con cierta periodicidad
    
    import os
    from time import time
    from time import sleep

    for i in range (60): # 333 es la cantidad máxima de llamados permitida a la API
        api_runner()
        print('API runner completado')
        sleep(60) # dormido por un minuto
        if i == 60:
            break
            
CSV con las recolecciones realizadas por la API

![image](https://user-images.githubusercontent.com/32172901/174460274-de4e19c8-07c5-4153-ad36-cfa7979d5c79.png)


Lectura del csv en otro df

    df_cripto = pd.read_csv(r'E:\Estudio\Análisis de datos\Proyectos\Crypto API\Cripto.csv')
    pd.set_option('display.float_format', lambda x: '%.5f' % x)   
    
## Transformación  de datos

Agrupación de los valores según la criptomoneda por medio del promedio de las variaciones para cada lapso

Creación de un arreglo para la selección de las columnas a utilizar, que en este caso son las del porcentaje de variación.

    col_names = df_cripto.columns
    keep=[column for column in col_names if 'quote.USD.percent_change_' in column]
    keep.insert(0,'name')

    # Creación del df_per_change con las columnas seleccionadas
    df_per_change = df_cripto.loc[:,keep]

    # Creación del df agrupado

    df_per_change = df_per_change.groupby('name', sort=False).mean()
    
## Creación de los gráficos de barras para cada uno de los lapsos

    import seaborn as sns
    import matplotlib.pyplot as plt

    # Cambio de los nombres de las columnas

    df_per_change = df_per_change.rename({'quote.USD.percent_change_1h':'1h','quote.USD.percent_change_24h':'24h','quote.USD.percent_change_7d':'7d','quote.USD.percent_change_30d':'30d','quote.USD.percent_change_60d':'60d','quote.USD.percent_change_90d':'90d'}, axis=1)

    # Gráfico de variación última una hora
    df_per_change = df_per_change.reset_index()
    sns.barplot(x='name', y = '1h', data =df_per_change )
    plt.title('Variaciones del precio última una hora')
    plt.xticks(rotation=45)
    
   ![1h](https://user-images.githubusercontent.com/32172901/174460318-8b826c9d-c2b2-405f-9edd-94faab026889.png)


    # Gráfico de variación últimas 24 horas

    sns.barplot(x='name', y = '24h', data =df_per_change )
    plt.title('Variaciones del precio últimas 24 horas')
    plt.xticks(rotation=45)
    
   ![24h](https://user-images.githubusercontent.com/32172901/174460362-d8e578be-1d01-4680-b252-df5282f49703.png)


    # Gráfico de variación últimos 7 días

    sns.barplot(x='name', y = '7d', data =df_per_change )
    plt.title('Variaciones del precio últimos 7 días')
    plt.xticks(rotation=45)
    
   ![7d](https://user-images.githubusercontent.com/32172901/174460469-31790519-bd29-4ef5-9e00-77a703708138.png)


    # Gráfico de variación últimos 30 días

    sns.barplot(x='name', y = '30d', data =df_per_change )
    plt.title('Variaciones del precio últimos 30 días')
    plt.xticks(rotation=45)
    
   ![30d](https://user-images.githubusercontent.com/32172901/174460470-af97515d-cce1-4ba3-b79f-53c1fb0642c9.png)


    # Gráfico de variación últimos 60 días

    sns.barplot(x='name', y = '60d', data =df_per_change )
    plt.title('Variaciones del precio últimos 60 días')
    plt.xticks(rotation=45)
    
   ![60d](https://user-images.githubusercontent.com/32172901/174460379-18216113-9d53-4f39-bfc5-9d501e06e2d6.png)


    # Gráfico de variación últimos 90 días

    sns.barplot(x='name', y = '90d', data =df_per_change )
    plt.title('Variaciones del precio últimos 90 días')
    plt.xticks(rotation=45)
    
   ![90d](https://user-images.githubusercontent.com/32172901/174460380-d687148a-26b1-49a3-956a-ef5cde4c1439.png)

Graficar el comportamiento del precio para el Bitcoin en el tiempo

df_bitcoin = df_cripto[['name','quote.USD.price','Timestamp']].query("name=='Bitcoin'")

    sns.set_theme(style='darkgrid')
    sns.lineplot(x='Timestamp', y = 'quote.USD.price', data=df_bitcoin)
    plt.title('Precio del Bitcoin')
    plt.xticks(rotation=90)
    
![Bitcoin_precio](https://user-images.githubusercontent.com/32172901/174460484-ce0b7a5a-5fa8-441e-9165-07e8488d609a.png)

Graficar el comportamiento de todos los precios de las criptomonedas

    df_precios = df_cripto[['name','quote.USD.price','Timestamp']]

    sns.set_theme(style='darkgrid')
    sns.lineplot(x='Timestamp', y = 'quote.USD.price', data=df_precios, hue = 'name')
    plt.title('Precios de las criptomonedas')
    plt.xticks(rotation=90)
    
![Criptomonedas_precio](https://user-images.githubusercontent.com/32172901/174460490-4e1464a8-bce6-44e2-937e-b368376c4b79.png)

Transformación y graficar el comportamiento de todos los precios de las criptomonedas
    import numpy as np

    df_precios['quote.USD.price_t'] = np.log10(df_precios['quote.USD.price'])

    sns.set_theme(style='darkgrid')
    sns.lineplot(x='Timestamp', y = 'quote.USD.price_t', data=df_precios, hue = 'name')
    plt.title('Precios de las criptomonedas (Log10)')
    plt.xticks(rotation=90)
    
![Criptomonedas_precio_tranformado](https://user-images.githubusercontent.com/32172901/174460498-1325290f-2d49-4167-b43d-34ccf761af01.png)


