import os
import requests
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
import torchxrayvision as xrv
import argparse
import pprint
from io import BytesIO
from pydicom import dcmread
from pydicom.pixel_data_handlers.util import apply_voi_lut
import warnings
from numpy import ndarray
from torchxrayvision.utils import normalize
# Argumentos do script
parser = argparse.ArgumentParser()
parser.add_argument('-weights', type=str, default="densenet121-res224-all", help='Modelo a ser utilizado.')
parser.add_argument('-feats', default=False, help='Se ativado, exibe características', action='store_true')
parser.add_argument('-cuda', default=False, help='Se ativado, utiliza GPU', action='store_true')
parser.add_argument('-resize', default=False, help='Se ativado, redimensiona a imagem', action='store_true')

cfg = parser.parse_args()

# Configurações do Orthanc
orthanc_url = 'http://localhost:8042'
orthanc_username = 'orthanc'
orthanc_password = 'orthanc'

def autenticar_orthanc():
    try:
        response = requests.get(orthanc_url, auth=(orthanc_username, orthanc_password))
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro de autenticação no Orthanc: {e}")
        return False

def listar_estudos():
    try:
        response = requests.get(f"{orthanc_url}/studies", auth=(orthanc_username, orthanc_password))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao listar estudos no Orthanc: {e}")
        return []

def obter_instancias(study_id):
    try:
        response = requests.get(f"{orthanc_url}/studies/{study_id}/instances", auth=(orthanc_username, orthanc_password))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter instâncias do estudo {study_id} no Orthanc: {e}")
        return []

def baixar_instancia(instance_id):
    try:
        url = f"{orthanc_url}/instances/{instance_id}/file"
        response = requests.get(url, auth=(orthanc_username, orthanc_password))
        response.raise_for_status()
        return BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar instância {instance_id} do Orthanc: {e}")
        return None

import os
import warnings
from numpy import ndarray
from torchxrayvision.utils import normalize

#Função read_xray_dcm fornecida por e-mail
def read_xray_dcm(path: os.PathLike) -> ndarray:
    """read a dicom-like file and convert to numpy array 

    Args:
        path (PathLike): path to the dicom file

    Returns:
        ndarray: 2D single array image for a dicom image scaled between -1024, 1024
    """
    try:
        import pydicom
    except ImportError:
        raise Exception("Missing Package Pydicom. Try installing it by running `pip install pydicom`.")

    # get the pixel array
    ds = pydicom.dcmread(path, force=True)

    # we have not tested RGB, YBR_FULL, or YBR_FULL_422 yet.
    if ds.PhotometricInterpretation not in ['MONOCHROME1', 'MONOCHROME2']:
        raise NotImplementedError(f'PhotometricInterpretation `{ds.PhotometricInterpretation}` is not yet supported.')

    data = ds.pixel_array
    
    # LUT for human friendly view
    data = pydicom.pixel_data_handlers.util.apply_voi_lut(data, ds, index=0)

    # `MONOCHROME1` have an inverted view; Bones are black; background is white
    # https://web.archive.org/web/20150920230923/http://www.mccauslandcenter.sc.edu/mricro/dicom/index.html
    if ds.PhotometricInterpretation == "MONOCHROME1":
        warnings.warn(f"Coverting MONOCHROME1 to MONOCHROME2 interpretation for file: {path}. Can be avoided by setting `fix_monochrome=False`")
        data = data.max() - data

    # normalize data to [-1024, 1024]
    data = normalize(data, data.max())
    return data


# Carregar o modelo
model = xrv.models.get_model(cfg.weights)

if autenticar_orthanc():
    estudos = listar_estudos()
    if estudos:
        for study_id in estudos:  # Itera sobre todos os estudos
            instancias = obter_instancias(study_id)
            for instance in instancias:  # Itera sobre todas as instâncias
                instance_id = instance['ID']
                dicom_file_like = baixar_instancia(instance_id)
                if dicom_file_like:
                    img = read_xray_dcm(dicom_file_like)

                    if len(img.shape) > 2:
                        img = img[:, :, 0]
                    if len(img.shape) < 2:
                        print("Erro: a imagem tem menos de 2 dimensões")
                        continue

                    img = img[None, :, :]

                    # Transformações
                    if cfg.resize:
                        transform = transforms.Compose([xrv.datasets.XRayCenterCrop(), xrv.datasets.XRayResizer(224)])
                    else:
                        transform = transforms.Compose([xrv.datasets.XRayCenterCrop()])

                    img = transform(img)

                    # Processar imagem com o modelo
                    img_tensor = torch.from_numpy(img).unsqueeze(0).float()
                    if cfg.cuda:
                        img_tensor = img_tensor.cuda()
                        model = model.cuda()

                    with torch.no_grad():
                        if cfg.feats:
                            feats = model.features(img_tensor)
                            feats = F.relu(feats, inplace=True)
                            feats = F.adaptive_avg_pool2d(feats, (1, 1))
                            output = {"feats": list(feats.cpu().detach().numpy().reshape(-1))}
                        else:
                            preds = model(img_tensor).cpu()
                            output = {"preds": dict(zip(xrv.datasets.default_pathologies, preds[0].detach().numpy()))}
                        
                        # Exibir resultados
                        if cfg.feats:
                            pprint.pprint(output)
                        else:
                            print(f"\nInstância: {instance_id}")
                            formatted_output = {'preds': output['preds']}
                            pprint.pprint(formatted_output)
