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
      self.ruta_input_xml_coreso = param.get(seccion, 'RUTA_INPUT_CORESO_XML')
      self.ruta_dic_nudox=param.get(seccion, 'RUTA_DICCIONARIO_NUDOS_X')

      self.directorio_input_xml_coreso=param.get(seccion, 'RUTA_INPUT_CORESO_XML')
      self.directorio_output_xml=param.get(seccion, 'RUTA_OUTPUT_XML')



      self.name_xml_capDoc_input = param.get(seccion, 'NOMBRE_XML_CAPDOC')
      self.name_xml_capDoc_re = param.get(seccion, 'NOMBRE_XML_CAPDOC_RE')
      self.name_xml_capDoc_ac = param.get(seccion, 'NOMBRE_XML_CAPDOC_AC')
      self.name_xml_cne_de = param.get(seccion, 'NOMBRE_XML_CNE_DET_REA')

class ColumnsDataFrame():

   dict_data = {'-1Sentidos': None, '00-01': None,
                '01-02': None, '02-03': None, '03-04': None,
                '04-05': None, '05-06': None, '06-07': None, '07-08': None, '08-09': None,
                '09-10': None, '10-11': None, '11-12': None, '12-13': None,
                '13-14': None, '14-15': None, '15-16': None,
                '16-17': None, '17-18': None, '18-19': None,
                '19-20': None, '20-21': None, '21-22': None, '22-23': None, '23-24': None, '24-25': None}

   columns = list(dict_data.keys())
   rename={'-1Sentidos':'Sentidos'}



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


class ElementosLimitantes():

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

class InfoXML():
   def __init__(self,periodo_star,periodo_end,es_fr=None,fr_es=None,es_pt=None,pt_es=None):
      """

      :param periodo_star:
      :param periodo_end:
      :param es_fr:
      :type es_fr: InfoSentidos
      :param fr_es:
      :type fr_es: InfoSentidos
      :param es_pt:
      :type es_pt: InfoSentidos
      :param pt_es:
      :type pt_es: InfoSentidos
      """
      self.periodo_star=periodo_star
      self.periodo_end= periodo_end
      self.es_fr=es_fr
      self.fr_es=fr_es
      self.es_pt=es_pt
      self.pt_es=pt_es

class InfoSentidos():
   def __init__(self,domain_in,domain_out,info_hora=[]):
      """

      :param domain_in:
      :type domain_in: Domain
      :param domain_out:
      :type domain_out: Domain
      :param info_hora:
      :type info_hora: list of InfoInterHora
      """
      self.domain_in = domain_in
      self.domain_out = domain_out
      self.info_hora=info_hora
      self.__sentido =None

   @property
   def sentido(self):
      return self.__sentido

   @sentido.getter
   def sentido(self):
      self.__sentido = '{} -> {}'.format(self.domain_out['id'],self.domain_in['id'])
      return self.__sentido

class InfoInterHora():
   def __init__(self,hora,potencia,aceptada=True):
      self.hora=hora
      self.potencia=potencia
      self.aceptada=aceptada
      self.__hora_label=None

   @property
   def hora_label(self):
      return self.__hora_label

   @hora_label.getter
   def hora_label(self):
      hora_in=self.hora
      hora_out = self.hora+1
      if hora_in<9:
         hora_in=str(hora_in).zfill(1)
      else:
         hora_in = str(hora_in)

      if hora_out<9:
         hora_out=str(hora_out).zfill(1)
      else:
         hora_out = str(hora_out)

      self.__hora_label = '{}-{}'.format(hora_in,hora_out)

      return self.__hora_label

class ReasonCode():
   def __init__(self,code,descrip):
      self.code=code
      self.descrip=descrip

class ExplatCode():
   def __init__(self,code,descrip):
      self.code=code
      self.descrip=descrip


def get_reason_explat_codes():
   try:
      param, seccion = lectura_archivo_configura(Rutas().ruta_fichero_config, 'PARAMETROS')
      reason_codes= param.get(seccion, 'REASON_CODE')
      list_reason_codes=[]
      list_explat_codes = []
      for x in reason_codes.split(';'):
         datos=x.split('-')
         list_reason_codes.append(ReasonCode(code=datos[1],descrip=datos[0]))


      explat_codes = param.get(seccion, 'EXPLANAT_CODE')
      for x in explat_codes.split(';'):
         datos = x.split('-')
         list_explat_codes.append(ExplatCode(code=datos[1], descrip=datos[0]))


      return  list_reason_codes, list_explat_codes

   except Exception as e:
      raise SystemError('error al obtener los Reason code y explanat code :{}'.format(e))