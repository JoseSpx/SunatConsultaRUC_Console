from bs4 import BeautifulSoup
import requests
import pytesseract as tess
from PIL import Image
from io import BytesIO
from helper import sunatconstants
import json

tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# urls
url_image = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/captcha?accion=image&magic=2'
url_info = 'http://www.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias?accion=consPorRuc&nroRuc={0}&codigo={1}'


ruc = '20100047218'
ruc = ruc.strip()

if len(ruc) != 11:
    print('RUC no válido')
    exit(0)

# Read Image SUNAT
response_image = requests.get(url_image)
cookies = response_image.cookies
img = Image.open(BytesIO(response_image.content))
img_text = tess.image_to_string(img)

# Read Info
url_info = url_info.format(ruc, img_text)
response_info = requests.get(url_info, cookies=cookies)
html_info = BeautifulSoup(response_info.content, 'html.parser')
table_info = html_info.find_all('tr')

if not table_info:
    print('Captcha no reconocido')
    exit(0)


class SunatInfo:
    def __init__(self):
        print('')


info_sunat = SunatInfo()

# RUC - Razon Social
numero_ruc = (table_info[0].find_all("td"))[1].contents[0]
info_sunat.ruc = numero_ruc.split('-')[0]
info_sunat.razon_social = numero_ruc.split('-')[1]

# Tipo Contribuyente
info_sunat.tipo_contribuyente = (table_info[1].find_all("td"))[1].contents[0]

sunat_cons = None
if ruc[0] == '1':
    # Verificar Nuevo RUS
    nuevo_rus = (table_info[3].find_all("td"))[2].contents[0].strip()
    if nuevo_rus == 'Afecto al Nuevo RUS:':
        sunat_cons = sunatconstants.PersonaNaturalNuevoRusConstant
    else:
        sunat_cons = sunatconstants.PersonaNaturalSinRusConstant
elif ruc[0] == '2':
    sunat_cons = sunatconstants.PersonaJuridicaConstant
else:
    print('RUC no válido')
    exit(0)

# Nombre Comercial
info_sunat.nombre_comercial = (table_info[sunat_cons.nombre_comercial.value].find_all("td"))[1].contents[0]

# Fecha Inscripcion
info_sunat.fecha_inscripcion = (table_info[sunat_cons.fecha_inscripcion.value].find_all("td"))[1].contents[0]

# Estado Contribuyente
info_sunat.estado_contibuyente = (table_info[sunat_cons.estado_contribuyente.value].find_all("td"))[1].contents[0]

# Condicion Contribuyente
info_sunat.condicion_contribuyente \
    = (table_info[sunat_cons.condicion_contribuyente.value].find_all("td"))[1].contents[0].replace('\r', '') \
    .replace('\n', '').strip()

# Domicilio Fiscal
domicilio = (table_info[sunat_cons.domicilio_fiscal.value].find_all("td"))[1].contents[0]
info_sunat.domicilio_fiscal = ' '.join(domicilio.split())

# Actividad Económica
act_ec_td = ((table_info[sunat_cons.actividad_economica.value].find_all("td"))[1])
info_sunat.actividad_economica = act_ec_td.find('select').find('option').contents[0]

print(json.dumps(info_sunat.__dict__))

'''
url = 'https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/frameCriterioBusqueda.jsp'
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')
img_html = soup.find('img')

print(text)
'''
