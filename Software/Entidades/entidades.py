from os.path import dirname, abspath
from datetime import datetime
import os as os

import ConfigParser as configparse


def lectura_archivo_configura(filename, seccion):
   """
   Funcion para leer los datos de configuracion (seccion= DATOS) del fichero de configuracion
   :param filename: PATH del fichero de configuracion
   :return: Retorna una intancia los parametros de configuracion
   """
   param=None
   seccion=seccion
   try:
      cfg = configparse.ConfigParser()
      #cfg.optionxform = str

      if not cfg.read([filename]):
         print "No existe el archivo en la ruta especificada {}".format(filename)
         raise  StandardError ("No existe el archivo de configuracion en la ruta especificada {}".format(filename))
      else:

         if not cfg.has_section(seccion):
            raise StandardError("No se ha encontrado la seccion indicada en el archivo de configuracion {}".format(seccion))
         else:
            secc = cfg.sections()
            secc = filter(lambda x: str.lower(x) == str.lower(seccion), secc)
            seccion=secc[0]
            param=cfg
   except Exception as e:
      print "ERROR: Mensaje: {}, TipoError: {}".format(e.message, e.__class__)
      raise StandardError ("Error en la lectura de archivos de configuracion: {} ",e.message)

   return param,seccion

class Rutas():
   def __init__(self):
      self.directorio_proyecto = dirname(dirname(dirname(abspath(__file__))))
      self.directorio_fich_configuracion = os.path.join(self.directorio_proyecto, 'Configuracion')
      self.ruta_fichero_config= os.path.join(self.directorio_fich_configuracion, 'Parametros.cfg')

      param, seccion = lectura_archivo_configura(self.ruta_fichero_config, 'RUTAS')

      self.ruta_excel_crack= param.get(seccion, 'RUTA_EXCEL_CRACK')

      self.ruta_idReport= param.get(seccion, 'RUTA_IDREPORT')
      self.ruta_input_xml_coreso = param.get(seccion, 'RUTA_IDREPORT')
      self.ruta_dic_nudox=param.get(seccion, 'RUTA_DICCIONARIO_NUDOS_X')

      self.directorio_input_xml_coreso=param.get(seccion, 'RUTA_INPUT_CORESO_XML')
      self.directorio_output_xml=param.get(seccion, 'RUTA_OUTPUT_XML')



      self.name_xml_capDoc_input = param.get(seccion, 'NOMBRE_XML_CAPDOC')
      self.name_xml_capDoc_re = param.get(seccion, 'NOMBRE_XML_CAPDOC_RE')
      self.name_xml_capDoc_ac = param.get(seccion, 'NOMBRE_XML_CAPDOC_AC')
      self.name_xml_cne_de = param.get(seccion, 'NOMBRE_XML_CNE_DET_REA')


class Domain():
   ES = {'id': 'ES', 'TSO': 'REE', 'mRID': '10YES-REE------0'}
   FR = {'id': 'FR', 'TSO': 'RTE', 'mRID': '10YFR-RTE------C'}
   PT = {'id': 'PT', 'TSO': 'REN', 'mRID': '10YPT-REN------W'}

   def get_list(self):
      list = []
      list.append(Domain.ES)
      list.append(Domain.FR)
      list.append(Domain.FR)

      return list


class ElementosLimintante():

   def __init__(self, BORDER, NPSSE_FROM, NPSSE_TO, CKT, LOCATION, ELEMENT, DESCRIPTION, IDREPORT):
      self.BORDER = BORDER
      self.NPSSE_FROM = NPSSE_FROM
      self.NPSSE_TO = NPSSE_TO
      self.CKT = CKT
      self.LOCATION = LOCATION
      self.ELEMENT = ELEMENT
      self.DESCRIPTION = DESCRIPTION
      self.IDREPORT = IDREPORT

class Contigencia():
   def __init__(self, mRID, NAME, NPSSE_FROM ,NPSSE_TO, CKT, LOCATION, ELEMENT, NUDO_X=None):
      self.mRID = mRID
      self.NAME = NAME
      self.NPSSE_FROM = NPSSE_FROM
      self.NPSSE_TO = NPSSE_TO
      self.CKT = CKT
      self.LOCATION = LOCATION
      self.ELEMENT = ELEMENT
      self.NUDO_X = NUDO_X