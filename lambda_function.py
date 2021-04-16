import json
import requests
import urllib.parse as urlparse
import urllib
import os
import boto3
import sys
from datetime import datetime, timedelta


s3 = boto3.resource('s3')


def GetPages(date):
    try:
        #Initial URL
        response_get = requests.get(url="https://dadosabertos.camara.leg.br/api/v2/proposicoes?dataInicio={0}&dataFim={1}&itens={2}&ordem=ASC&ordenarPor=id".format(date, date, os.environ['ITENS_PAGINA']))
    
        #Primeira chamada        
        json_props = json.loads(response_get.text)
        
        #Primeira Pagina
        first_page_url = json_props['links'][2]['href']
        parsed_first = urlparse.urlparse(first_page_url).query
        first_page=urllib.parse.parse_qs(parsed_first)['pagina'][0]
        
        #Ultima Pagina
        last_page_url = json_props['links'][3]['href']
        parsed_last = urlparse.urlparse(last_page_url).query
        last_page=urllib.parse.parse_qs(parsed_last)['pagina'][0]
        
        #Proxima Pagina
        next_page_url = json_props['links'][1]['href']
        
        #Gerando Arquivos e Escrevendo no bucket
        GenerateJsonFile(first_page,last_page,response_get,json_props)

    except Exception as e:
        print(e.__class__)
        print(e)
    
def GenerateJsonFile(first_page,last_page,json_boject,json_props):
    try:
        for pages in range(int(first_page), int(last_page)):
            next_page_url = json_props['links'][1]['href']
            response_next_get = requests.get(url=next_page_url)
            json_props = json.loads(response_next_get.text)
        
        #Montando nome do Arquivo
        ano = date.split(sep="-")[0]
        mes = date.split(sep="-")[1]
        dia = date.split(sep="-")[2]        
        json_file_name = "raw/camara/proposicoes/json/{0}/{1}/{2}/{3}.json".format(ano,mes,dia,str(json_props["dados"][0]["id"]))

        #Escrevendo no bucket S3     
        s3.Object(os.environ['BUCKET'], json_file_name).put(Body=(bytes(json.dumps(json_props).encode('UTF-8'))))
    
    except Exception as e:
        print(e.__class__)
        print(e)

def lambda_handler(event, context):
    date = (datetime.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
    GetPages(date)
