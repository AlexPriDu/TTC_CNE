import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import re
from Software.Entidades.entidades import Domain, InfoXML, InfoSentidos, InfoInterHora, ColumnsDataFrame
import pandas as pd
import copy


def lectura_SWE_D2_CapDoc_Prop(path=None):
   try:
      # path=path.decode('string_escape')
      # path=os.path.normpath(path)
      if not os.path.exists(path):
         raise SystemError('El fichero no existe: {}'.format(path))

      expe='(?<=Capacity_MarketDocument\s)(\w+\W+)[^>]*'

      file = open(path, 'r')
      text = file.read().strip()
      file.close()

      m = re.search(expe, text)
      text =text.replace(m.group(0),'')

      raiz = ET.fromstring(text)
      start = raiz.find('./period.timeInterval/start').text
      end = raiz.find('period.timeInterval/end').text
      select_domian= select_case()
      time_serias=raiz.findall("./TimeSeries")
      info_xml=InfoXML(periodo_star=start,periodo_end=end)

      for serie in time_serias:
         list_info_hora = create_listInfo()
         domain_in = serie.find('in_Domain.mRID')
         domain_in=find_domian(domain_in.text)
         domain_out = serie.find('out_Domain.mRID')
         domain_out = find_domian(domain_out.text)
         domain=domain_in+domain_out
         for period in serie.findall('Period'):
            for point in period.findall('Point'):
               hora=int(point.find('position').text)
               potencia=float(point.find('quantity').text)
               info_hora = filter(lambda x: x.hora == hora, list_info_hora)
               if info_hora.__len__()>0:
                  info_hora=info_hora[0]
                  info_hora.potencia=potencia
                  info_hora.aceptada=True
         info_xml = select_domian[domain](info_xml,list_info_hora)

      return info_xml


   except Exception as e:
      raise SystemError('Error al leer  SWE_D2_CapDoc_Prop :{}'.format(e))

def select_case():
   dict = {'ESFR': get_domainFRES,
           'FRES': get_domainESFR,
           'ESPT': get_domainESPT,
           'PTES': get_domainPTES }
   return dict

def get_domainFRES(info_xml, list_info_hora):
   """

   :param info_xml:
   :type info_xml: InfoXML
   :return:
   """
   infoSentidos = InfoSentidos(domain_in=Domain().FR, domain_out=Domain().ES, info_hora=list_info_hora)
   info_xml.fr_es = infoSentidos
   return info_xml

def get_domainESFR(info_xml,list_info_hora):
   """

      :param info_xml:
      :type info_xml: InfoXML
      :return:
      """
   infoSentidos=InfoSentidos(domain_in=Domain().ES, domain_out=Domain().FR, info_hora=list_info_hora)
   info_xml.es_fr=infoSentidos
   return  info_xml

def get_domainESPT(info_xml,list_info_hora):
   """

      :param info_xml:
      :type info_xml: InfoXML
      :return:
      """

   infoSentidos = InfoSentidos(domain_in=Domain().ES, domain_out=Domain().PT, info_hora=list_info_hora)
   info_xml.es_pt = infoSentidos
   return info_xml

def get_domainPTES(info_xml,list_info_hora):
   """

      :param info_xml:
      :type info_xml: InfoXML
      :return:
      """
   infoSentidos = InfoSentidos(domain_in=Domain().PT, domain_out=Domain().ES, info_hora=list_info_hora)
   info_xml.pt_es = infoSentidos
   return info_xml

def find_domian(text):
   """

   :param text:
   :type text: str
   :return:
   """
   if text.find('ES') != -1:
      return 'ES'
   elif text.find('PT') != -1:
      return 'PT'
   elif text.find('FR') != -1:
      return 'FR'
   else:
      raise SystemError('No se ha encontrado del Domain en el texto : {}'.format(text))

def create_listInfo():
   res=[]

   for x in range(0,25,1):
      res.append(InfoInterHora(hora=x,potencia=None,aceptada=False))



   return res

def InfoXML_to_Dataframe(info_xml):
   """

   :param info_xml:
   :type info_xml: InfoXML
   :return:
   """
   try:
      df_infoXML = pd.DataFrame()
      columns_df = ['Sentidos', '00-01',
                    '01-02', '02-03', '03-04',
                    '04-05', '05-06', '06-07', '07-08', '08-09',
                    '09-10', '10-11', '11-12', '12-13',
                    '13-14', '14-15', '15-16',
                    '16-17', '17-18', '18-19',
                    '19-20', '20-21', '21-22', '22-23', '23-24', '24-25']



      info_ptEs = info_xml.pt_es
      info_esPt = info_xml.es_pt
      info_frEs = info_xml.fr_es
      info_esFr = info_xml.es_fr
      list_data=[]

      for info in [info_ptEs,info_esPt,info_frEs,info_esFr]:  # type: InfoSentidos
         pass
         sentido=info.sentido
         hora0=filter(lambda x: x.hora==0,info.info_hora)[0].potencia
         hora1 = filter(lambda x: x.hora == 1, info.info_hora)[0].potencia
         hora2 = filter(lambda x: x.hora == 2, info.info_hora)[0].potencia
         hora3 = filter(lambda x: x.hora == 3, info.info_hora)[0].potencia
         hora4 = filter(lambda x: x.hora == 4, info.info_hora)[0].potencia
         hora5 = filter(lambda x: x.hora == 5, info.info_hora)[0].potencia
         hora6 = filter(lambda x: x.hora == 6, info.info_hora)[0].potencia
         hora7 = filter(lambda x: x.hora == 7, info.info_hora)[0].potencia
         hora8 = filter(lambda x: x.hora == 8, info.info_hora)[0].potencia
         hora9 = filter(lambda x: x.hora == 9, info.info_hora)[0].potencia
         hora10 = filter(lambda x: x.hora == 10, info.info_hora)[0].potencia
         hora11 = filter(lambda x: x.hora == 11, info.info_hora)[0].potencia
         hora12 = filter(lambda x: x.hora == 12, info.info_hora)[0].potencia
         hora13 = filter(lambda x: x.hora == 13, info.info_hora)[0].potencia
         hora14 = filter(lambda x: x.hora == 14, info.info_hora)[0].potencia
         hora15 = filter(lambda x: x.hora == 15, info.info_hora)[0].potencia
         hora16 = filter(lambda x: x.hora == 16, info.info_hora)[0].potencia
         hora17 = filter(lambda x: x.hora == 17, info.info_hora)[0].potencia
         hora18 = filter(lambda x: x.hora == 18, info.info_hora)[0].potencia
         hora19 = filter(lambda x: x.hora == 19, info.info_hora)[0].potencia
         hora20 = filter(lambda x: x.hora == 20, info.info_hora)[0].potencia
         hora21 = filter(lambda x: x.hora == 21, info.info_hora)[0].potencia
         hora22 = filter(lambda x: x.hora == 22, info.info_hora)[0].potencia
         hora23 = filter(lambda x: x.hora == 23, info.info_hora)[0].potencia
         hora24 = filter(lambda x: x.hora == 24, info.info_hora)[0].potencia

         dict_data_info=copy.deepcopy(ColumnsDataFrame().dict_data)
         dict_data_info['-1Sentidos']=sentido
         dict_data_info['00-01'] = hora0
         dict_data_info['01-02'] = hora1
         dict_data_info['02-03'] = hora2
         dict_data_info['03-04'] = hora3
         dict_data_info['04-05'] = hora4
         dict_data_info['05-06'] = hora5
         dict_data_info['06-07'] = hora6
         dict_data_info['07-08'] = hora7
         dict_data_info['08-09'] = hora8
         dict_data_info['09-10'] = hora9
         dict_data_info['10-11'] = hora10
         dict_data_info['11-12'] = hora11
         dict_data_info['12-13'] = hora12
         dict_data_info['13-14'] = hora13
         dict_data_info['14-15'] = hora14
         dict_data_info['15-16'] = hora15
         dict_data_info['16-17'] = hora16
         dict_data_info['17-18'] = hora17
         dict_data_info['18-19'] = hora18
         dict_data_info['19-20'] = hora19
         dict_data_info['20-21'] = hora20
         dict_data_info['21-22'] = hora21
         dict_data_info['22-23'] = hora22
         dict_data_info['23-24'] = hora23
         dict_data_info['24-25'] = hora24

         list_data.append(dict_data_info)

      df_infoXML = pd.DataFrame(list_data)
      df_infoXML =df_infoXML.rename(index=str, columns=ColumnsDataFrame().rename)

      return df_infoXML



   except Exception as e:
      raise SystemError('Error al convertir el SWE_D2_CapDoc_Prop a Dataframe: {}'.format(e))