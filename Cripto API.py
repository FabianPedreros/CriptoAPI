# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 22:42:30 2022

@author: usuario
"""
### Crypto API ###

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
  
# Normalización de los datos, debido a que son almacenados en un directorio por la estructura Json

import pandas as pd
df=pd.json_normalize(data['data'])


#%%

# Ingresar al df la fecha y hora de la consulta al API, se añade la conversión a la timezone  de Bogotá, Colombia.

df['Timestamp']=pd.to_datetime('now').tz_localize('UTC').tz_convert('America/Bogota')


#%%
# Creación de una función que se encargue de consultar el API y añadir la nueva información al df

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
    
#%%
# Creación de el loop para que la función se ejecute una cantidad de veces dada y con cierta periodicidad
    
import os
from time import time
from time import sleep

for i in range (60): # 333 es la cantidad máxima de llamados permitida a la API
    api_runner()
    print('API runner completado')
    sleep(60) # dormido por un minuto
    if i == 60:
        break
    
#%%
# Lectura del csv en otro df
df_cripto = pd.read_csv(r'E:\Estudio\Análisis de datos\Proyectos\Crypto API\Cripto.csv')
pd.set_option('display.float_format', lambda x: '%.5f' % x)

#%%
# Agrupación de los valores según la criptomoneda por medio del promedio de las variaciones para cada lapso

# Creación de un arreglo para la selección de las columnas a utilizar, que en este caso son las del porcentaje de variación.

col_names = df_cripto.columns
keep=[column for column in col_names if 'quote.USD.percent_change_' in column]
keep.insert(0,'name')

# Creación del df_per_change con las columnas seleccionadas
df_per_change = df_cripto.loc[:,keep]

# Creación del df agrupado

df_per_change = df_per_change.groupby('name', sort=False).mean()

#%%
# Creación de los gráficos de barras para cada uno de los lapsos

import seaborn as sns
import matplotlib.pyplot as plt

# Cambio de los nombres de las columnas

df_per_change = df_per_change.rename({'quote.USD.percent_change_1h':'1h','quote.USD.percent_change_24h':'24h','quote.USD.percent_change_7d':'7d','quote.USD.percent_change_30d':'30d','quote.USD.percent_change_60d':'60d','quote.USD.percent_change_90d':'90d'}, axis=1)

# Gráfico de variación última una hora
df_per_change = df_per_change.reset_index()
sns.barplot(x='name', y = '1h', data =df_per_change )
plt.title('Variaciones del precio última una hora')
plt.xticks(rotation=45)

# Gráfico de variación últimas 24 horas

sns.barplot(x='name', y = '24h', data =df_per_change )
plt.title('Variaciones del precio últimas 24 horas')
plt.xticks(rotation=45)

# Gráfico de variación últimos 7 días

sns.barplot(x='name', y = '7d', data =df_per_change )
plt.title('Variaciones del precio últimos 7 días')
plt.xticks(rotation=45)

# Gráfico de variación últimos 30 días

sns.barplot(x='name', y = '30d', data =df_per_change )
plt.title('Variaciones del precio últimos 30 días')
plt.xticks(rotation=45)

# Gráfico de variación últimos 60 días

sns.barplot(x='name', y = '60d', data =df_per_change )
plt.title('Variaciones del precio últimos 60 días')
plt.xticks(rotation=45)

# Gráfico de variación últimos 90 días

sns.barplot(x='name', y = '90d', data =df_per_change )
plt.title('Variaciones del precio últimos 90 días')
plt.xticks(rotation=45)

# Graficar el comportamiento del precio para el Bitcoin en el tiempo

df_bitcoin = df_cripto[['name','quote.USD.price','Timestamp']].query("name=='Bitcoin'")

sns.set_theme(style='darkgrid')
sns.lineplot(x='Timestamp', y = 'quote.USD.price', data=df_bitcoin)
plt.title('Precio del Bitcoin')
plt.xticks(rotation=90)


# Graficar el comportamiento de todos los precios de las criptomonedas

df_precios = df_cripto[['name','quote.USD.price','Timestamp']]

sns.set_theme(style='darkgrid')
sns.lineplot(x='Timestamp', y = 'quote.USD.price', data=df_precios, hue = 'name')
plt.title('Precios de las criptomonedas')
plt.xticks(rotation=90)

# Transformación y graficar el comportamiento de todos los precios de las criptomonedas
import numpy as np


df_precios['quote.USD.price_t'] = np.log10(df_precios['quote.USD.price'])

sns.set_theme(style='darkgrid')
sns.lineplot(x='Timestamp', y = 'quote.USD.price_t', data=df_precios, hue = 'name')
plt.title('Precios de las criptomonedas (Log10)')
plt.xticks(rotation=90)






































