import json
import requests
import urllib.parse as urlparse
import urllib
import os
import boto3

s3 = boto3.resource('s3')

def GetPages():
    #Initial URL
    response_get = requests.get(url="https://dadosabertos.camara.leg.br/api/v2/proposicoes?dataInicio={0}&dataFim={1}&itens={2}&ordem=ASC&ordenarPor=id".format(os.environ['DATA_INICIO'],os.environ['DATA_FIM'],os.environ['ITENS_PAGINA']))
    
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
    
#Escrita no Bucket S3
def GenerateJsonFile(first_page,last_page,json_boject,json_props):
    for pages in range(int(first_page), int(last_page)):
        next_page_url = json_props['links'][1]['href']
        response_next_get = requests.get(url=next_page_url)
        json_props = json.loads(response_next_get.text)
        
        #Montando nome do Arquivo
        ano = os.environ['DATA_INICIO'].split(sep="-")[0]
        mes = os.environ['DATA_INICIO'].split(sep="-")[1]
        dia = os.environ['DATA_INICIO'].split(sep="-")[2]
        
        json_file_name = "raw/camara/proposicoes/json/{0}/{1}/{2}/{3}.json".format(ano,mes,dia,str(json_props["dados"][0]["id"]))
            
        s3.Object(os.environ['BUCKET'], json_file_name).put(Body=(bytes(json.dumps(json_props).encode('UTF-8'))))
        

def lambda_handler(event, context):
    GetPages()
