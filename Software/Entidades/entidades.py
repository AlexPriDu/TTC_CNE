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
      self.ruta_dic_nudox=param.get(seccion, 'RUTA_DICCIONARIO_NUDOS_X')

      self.directorio_input_xml_coreso=param.get(seccion, 'RUTA_INPUT_CORESO_XML')
      self.directorio_output_xml=param.get(seccion, 'RUTA_OUTPUT_XML')


      #
      # self.name_xml_capDoc_input = param.get(seccion, 'NOMBRE_XML_CAPDOC')
      # self.name_xml_capDoc_re = param.get(seccion, 'NOMBRE_XML_CAPDOC_RE')
      # self.name_xml_capDoc_ac = param.get(seccion, 'NOMBRE_XML_CAPDOC_AC')
      # self.name_xml_cne_de = param.get(seccion, 'NOMBRE_XML_CNE_DET_REA')

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
   def __init__(self,mRID,periodo_star,periodo_end,revisionNumber,es_fr=None,fr_es=None,es_pt=None,pt_es=None):
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
      self.mRID=mRID
      self.revisionNumber=revisionNumber
      self.es_fr=es_fr
      self.fr_es=fr_es
      self.es_pt=es_pt
      self.pt_es=pt_es

   @property
   def fecha_end(self):
      return self._fecha_end

   @fecha_end.getter
   def fecha_end(self):
      self._fecha_end = datetime.strptime(self.periodo_end,'%Y-%m-%dT%H:%MZ')
      return self._fecha_end

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

   def __init__(self,hora,potencia,potencia_old=None,aceptada=True):
      self.hora=hora
      self.potencia=potencia
      self.potencia_old = potencia_old
      self.aceptada=aceptada

      self.__rea_code=None
      self.__rea_coment = None
      self.__rea_text = None

      self.__explat_code = None
      self.__explat_coment = None
      self.__explat_text = None

      self.__cont_mRid = None
      self.__cont_name = None

      self.__mont_mRid = None
      self.__mont_name = None
      self.__mont_domainIN = None
      self.__mont_domainOUT= None

      self.__hora_label=None
      self.elements_UI=None

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

   @property
   def rea_code(self):
      return self.__rea_code

   @rea_code.getter
   def rea_code(self):
      if self.__rea_code == None:
         index = self.elements_UI.line_reason_code.currentIndex()
         data = self.elements_UI.line_reason_code.itemData(index)
         if data != None:
            self.__rea_code = data.code
         else:
            self.__rea_code = data
      return self.__rea_code

   @property
   def rea_coment(self):
      return self.__rea_coment

   @rea_coment.getter
   def rea_coment(self):
      if self.__rea_coment == None:
         index = self.elements_UI.line_reason_code.currentIndex()
         data = self.elements_UI.line_reason_code.itemData(index)
         if data != None:
            self.__rea_coment = data.descrip
         else:
            self.__rea_coment = data

      return self.__rea_coment

   @property
   def rea_text(self):
      return self.__rea_text

   @rea_text.getter
   def rea_text(self):
      self.__rea_text=self.elements_UI.line_reason_text.toPlainText()
      return self.__rea_text

   @property
   def explat_code(self):
      return self.__explat_code

   @explat_code.getter
   def explat_code (self):
      if self.__explat_code == None:
         index = self.elements_UI.line_expla_code.currentIndex()
         data = self.elements_UI.line_expla_code.itemData(index)
         if data != None:
            self.__explat_code=data.code
         else:
            self.__explat_code =None
      return self.__explat_code

   @property
   def explat_coment(self):
      return self.__explat_coment

   @explat_coment.getter
   def explat_coment(self):
      if self.__explat_coment == None:
         index = self.elements_UI.line_expla_code.currentIndex()
         data = self.elements_UI.line_expla_code.itemData(index)
         self.__explat_coment = data.descrip
      return self.__explat_coment

   @property
   def explat_text(self):
      return self.__explat_text

   @explat_text.getter
   def explat_text(self):
      self.__explat_text=self.elements_UI.line_expla_text.toPlainText()
      return self.__explat_text

   @property
   def cont_mRid(self):
      return self.__cont_mRid

   @cont_mRid.getter
   def cont_mRid(self):
      if self.__cont_mRid == None:
         index = self.elements_UI.combox_con_limitante.currentIndex()
         data = self.elements_UI.combox_con_limitante.itemData(index)
         if data != None:
            self.__cont_mRid = data['mRID CO Dict']
         else:
            self.__cont_mRid = None
      return self.__cont_mRid

   @property
   def cont_name(self):
      return self.__cont_name

   @cont_name.getter
   def cont_name(self):
      if self.__cont_name == None:
         index = self.elements_UI.combox_con_limitante.currentIndex()
         data = self.elements_UI.combox_con_limitante.itemData(index)
         if data != None:
            self.__cont_name = data['name CO Dict']
         else:
            self.__cont_name = None
      return self.__cont_name

   @property
   def mont_mRid(self):
      return self.__mont_mRid

   @mont_mRid.getter
   def mont_mRid(self):
      if self.__mont_mRid == None:
         index = self.elements_UI.combox_ele_limitante.currentIndex()
         data = self.elements_UI.combox_ele_limitante.itemData(index)
         if data != None:
            self.__mont_mRid = data['Cim ID']
         else:
            self.__mont_mRid = None
      return self.__mont_mRid

   @property
   def mont_name(self):
      return self.__mont_name

   @mont_name.getter
   def mont_name(self):
      if self.__mont_name == None:
         index = self.elements_UI.combox_ele_limitante.currentIndex()
         data = self.elements_UI.combox_ele_limitante.itemData(index)
         if data != None:
            self.__mont_name = data['DESCRIPTION'].replace('[','').replace(']','')
         else:
            self.__mont_name = None
      return self.__mont_name

   @property
   def mont_domainIN(self):
      return self.__mont_domainIN

   @mont_domainIN.getter
   def mont_domainIN(self):
      if self.__mont_domainIN == None:
         index = self.elements_UI.combox_ele_limitante.currentIndex()
         data = self.elements_UI.combox_ele_limitante.itemData(index)
         if data != None:
            lacation = data['LOCATION'].split('-')
            if lacation[1]=='ES':
               self.__mont_domainIN=Domain.ES['mRID']
            elif lacation[1] == 'PT':
               self.__mont_domainIN = Domain.PT['mRID']
            else:
               self.__mont_domainIN = Domain.FR['mRID']
         else:
            self.__mont_domainIN= None

      return self.__mont_domainIN

   @property
   def mont_domainOUT(self):
      return self.__mont_domainOUT

   @mont_domainOUT.getter
   def mont_domainOUT(self):
      if self.__mont_domainOUT == None:
         index = self.elements_UI.combox_ele_limitante.currentIndex()
         data = self.elements_UI.combox_ele_limitante.itemData(index)
         if data != None:
            lacation = data['LOCATION'].split('-')
            if lacation[0] == 'ES':
               self.__mont_domainOUT = Domain.ES['mRID']
            elif lacation[0] == 'PT':
               self.__mont_domainOUT = Domain.PT['mRID']
            else:
               self.__mont_domainOUT = Domain.FR['mRID']
         else:
            self.__mont_domainOUT= None

      return self.__mont_domainOUT

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

class ParamXML_CapDoc():
   def __init__(self):
      self.namespace_label = 'urn:iec62325.351:tc57wg16:451-3:capacitydocument:8:0'
      self.namespace='{urn:iec62325.351:tc57wg16:451-3:capacitydocument:8:0}'
      self.atribute_capDoc={'xsi:schemaLocation':'urn:iec62325.351:tc57wg16:451-3:capacitydocument:8:0 iec62325-451-3-capacity_v8_0.xsd',
                           'xmlns':'urn:iec62325.351:tc57wg16:451-3:capacitydocument:8:0','xmlns:xsi':'http://www.w3.org/2001/XMLSchema-instance'}
      self.type_doc='A26'

      self.MarketParticipant_Role_SO='A04' #System Operator"
      self.MarketParticipant_Role_CC = 'A36' #Capacity Coordinator"

      self.MarketParticipant_mRID_SO = '10XES-REE------E'  # System Operator"
      self.MarketParticipant_mRID_CC = '22XCORESO------S'  # Capacity Coordinator"
      self.processType='A48'
      self.type='A48'
      self.domain_mRID='10YCB-FR-ES-PT-S'
      self.docStatus_Reject='A34'
      self.docStatus_Acept = 'A37'
      self.mRID_REE='REE-%Y%m%d-SWECCD2-F019'
      self.mRID_CORESO = 'Coreso-%Y%m%d-SWECCD2-F019'
      self.codingScheme = 'A01'

      self.TimeSeries_mRID='REE-Timeseries'
      self.businessType = 'A81'
      self.product='8716867000016'
      self.measure_Unit='MAW'
      self.resolution='PT60M'
      self.reason_code_CapDoc='A95'
      self.reason_text_CapDoc = 'REE'

      self.mRID_Timeseries='REE-Timeseries'

      self.namespace_label_CNE = 'urn:iec62325.351:tc57wg16:451-n:cnedocument:2:0'
      self.namespace_CNE = '{urn:iec62325.351:tc57wg16:451-n:cnedocument:2:0'
      self.atribute_CNE = {
         'xsi:schemaLocation': 'urn:iec62325.351:tc57wg16:451-n:cnedocument:2:0 iec62325-451-n-cne_v2_0_draft.xsd',
         'xmlns': 'urn:iec62325.351:tc57wg16:451-n:cnedocument:2:0',
         'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
      self.type_doc_CNE = 'B06'

      self.mRID_REE_CNE = 'REE-%Y%m%d-SWECCD2-F020'
      self.businessType_CNE_TimeSerie = 'B37'
      self.businessType_CNE_Point = 'B37'
      self.curveType_CNE = 'A02'
      self.mRID_Constraint_Co = 'REE-Constraint_Series-CoList-'
      self.mRID_Constraint_Mon = 'REE-Constraint_Series-MRList-'
      self.mRID_Constraint_CoMon = 'REE-Constraint_Series-CoMR-'
      self.mRID_Constraint_Nan = 'REE-Constraint_Series-'


