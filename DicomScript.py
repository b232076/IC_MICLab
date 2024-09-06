import os
import requests
from requests.auth import HTTPBasicAuth

# Configurações do servidor Orthanc
ORTHANC_URL = 'http://localhost:8042'  # Substitua pelo URL do seu servidor Orthanc
ORTHANC_USERNAME = 'orthanc'           # Substitua pelo seu usuário Orthanc
ORTHANC_PASSWORD = 'orthanc'           # Substitua pela sua senha Orthanc

def upload_dicom(file_path):
    url = f'{ORTHANC_URL}/instances'
    
    try:
        # Envia o arquivo DICOM
        with open(file_path, 'rb') as dicom_file:
            response = requests.post(url, files={'file': dicom_file}, auth=HTTPBasicAuth(ORTHANC_USERNAME, ORTHANC_PASSWORD))

        if response.status_code == 200:
            print(f'Arquivo {file_path} enviado com sucesso!')
            if response.content:
                try:
                    print('Resposta do servidor:', response.json())
                except ValueError:
                    print('Resposta do servidor não é um JSON válido:', response.content)
            else:
                print('Resposta do servidor está vazia.')
        else:
            print(f'Erro ao enviar o arquivo {file_path}: {response.status_code}')
            print('Resposta do servidor:', response.text)
    except Exception as e:
        print(f'Erro ao enviar o arquivo {file_path}: {e}')

def upload_all_dicoms(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.dcm'):
                file_path = os.path.join(root, file)
                print(f'Processando arquivo: {file_path}')
                upload_dicom(file_path)

# Caminho da pasta contendo arquivos DICOM
dicom_directory = '/home/beavpm/DICOM' 
upload_all_dicoms(dicom_directory)