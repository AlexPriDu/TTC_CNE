import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import re
from Software.Entidades.entidades import Domain, InfoXML, InfoSentidos, InfoInterHora, ColumnsDataFrame, ParamXML_CapDoc
import pandas as pd
import copy
import pytz, datetime


def  gte_SWE_D2_CapDoc_Prop_text(path):
   """

   :param path:
   :return:
   :rtype: ET.Element
   """
   try:
      if not os.path.exists(path):
         raise SystemError('El fichero no existe: {}'.format(path))

      expe = '(?<=Capacity_MarketDocument\s)(\w+\W+)[^>]*'

      file = open(path, 'r')
      text = file.read().strip()
      file.close()

      m = re.search(expe, text)
      guid = m.group(0)
      text = text.replace(m.group(0), '')

      raiz = ET.fromstring(text)
      return  raiz, guid
   except Exception as e:
      raise SystemError('ERROR al gte_SWE_D2_CapDoc_Prop: {}'.format(e))

def gte_SWE_D2_CapDoc_Prop_tree(path):
   try:
      namespace=''

      tree = ET.ElementTree()
      raiz=tree.parse(path)
      namespace=raiz.tag
      namespace=namespace.replace('Capacity_MarketDocument','')

      return raiz,namespace
   except Exception as e:
      raise SystemError('Error al gte_SWE_D2_CapDoc_Prop_tree:{}'.format(e))

def lectura_SWE_D2_CapDoc_Prop_tree(path=None):
   try:

      #raiz, namespace=gte_SWE_D2_CapDoc_Prop_tree(path=path)

      tree = ET.ElementTree()
      raiz = tree.parse(path)
      namespace=ParamXML_CapDoc().namespace
      mrid=raiz.find('{}mRID'.format(namespace)).text
      revisonNumbre=raiz.find('{}revisionNumber'.format(namespace)).text
      start = raiz.find('{}period.timeInterval/{}start'.format(namespace,namespace)).text
      end = raiz.find('{}period.timeInterval/{}end'.format(namespace,namespace)).text
      select_domian= select_case()
      time_serias=raiz.findall("{}TimeSeries".format(namespace))
      info_xml=InfoXML(periodo_star=start,periodo_end=end, mRID=mrid, revisionNumber=revisonNumbre)

      for serie in time_serias:
         list_info_hora = create_listInfo()
         domain_in = serie.find('{}in_Domain.mRID'.format(namespace))
         domain_in=find_domian(domain_in.text)
         domain_out = serie.find('{}out_Domain.mRID'.format(namespace))
         domain_out = find_domian(domain_out.text)
         domain=domain_in+domain_out
         for period in serie.findall('{}Period'.format(namespace)):
            for point in period.findall('{}Point'.format(namespace)):
               hora=int(point.find('{}position'.format(namespace)).text)
               potencia=float(point.find('{}quantity'.format(namespace)).text)
               info_hora = filter(lambda x: x.hora == hora-1, list_info_hora)
               if info_hora.__len__()>0:
                  info_hora=info_hora[0]
                  info_hora.potencia=potencia
                  info_hora.aceptada=True
         info_xml = select_domian[domain](info_xml,list_info_hora)

      return info_xml


   except Exception as e:
      raise SystemError('Error al leer  SWE_D2_CapDoc_Prop :{}'.format(e))

def lectura_SWE_D2_CapDoc_Prop(path=None):
   try:
      raiz, guid = gte_SWE_D2_CapDoc_Prop_text(path)

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

      return info_xml, guid


   except Exception as e:
      raise SystemError('Error al leer  SWE_D2_CapDoc_Prop :{}'.format(e))

def select_case():
   dict = {'ESFR': get_domainESFR,
           'FRES': get_domainFRES,
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
      res.append(InfoInterHora(hora=x,potencia=None,aceptada=True))



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

def create_XML_CapDoc_by_Plantilla(path_input, path_output, info_xml, acept=True):
   """

   :param path_input:
   :param path_output:
   :param info_xml:
   :type info_xml: InfoXML
   :param acept:
   :return:
   """
   try:
      datosXML = ParamXML_CapDoc()
      ET.register_namespace('', datosXML.namespace_label)
      tree = ET.ElementTree()
      raiz = tree.parse(path_input)
      namespace = raiz.tag
      namespace = namespace.replace('Capacity_MarketDocument', '')

      raiz.find('{}mRID'.format(namespace)).text=info_xml.mRID
      raiz.find('{}revisionNumber'.format(namespace)).text = '1'

      raiz.find('{}sender_MarketParticipant.mRID'.format(namespace)).text = datosXML.MarketParticipant_mRID_SO
      raiz.find('{}sender_MarketParticipant.marketRole.type'.format(namespace)).text=datosXML.MarketParticipant_Role_SO

      raiz.find('{}receiver_MarketParticipant.mRID'.format(namespace)).text=datosXML.MarketParticipant_mRID_CC
      raiz.find('{}receiver_MarketParticipant.marketRole.type'.format(namespace)).text=datosXML.MarketParticipant_Role_CC

      local = pytz.timezone("Europe/Madrid")
      naive = datetime.datetime.now()
      local_dt = local.localize(naive, is_dst=None)
      utc_dt = local_dt.astimezone(pytz.utc)

      datime_zulu=utc_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

      raiz.find('{}createdDateTime'.format(namespace, namespace)).text = datime_zulu

      doc_estus_value=datosXML.docStatus_Acept if acept else  datosXML.docStatus_Reject
      raiz.find('{}docStatus/{}value'.format(namespace,namespace)).text=doc_estus_value


      new = ET.SubElement(raiz,'{}received_MarketDocument.mRID'.format(namespace))
      new.text = info_xml.mRID
      #raiz.append(new)

      # raiz.find('{}received_MarketDocument.mRID'.format(namespace)).text = info_xml.mRID
      # raiz.find('{}received_MarketDocument.revisionNumber'.format(namespace)).text = info_xml.revisionNumber

      raiz.find('{}period.timeInterval/{}start'.format(namespace,namespace)).text = info_xml.periodo_star
      raiz.find('{}period.timeInterval/{}end'.format(namespace,namespace)).text = info_xml.periodo_end

      if acept != True:
         i=1
         for time_serie in raiz.findall('{}TimeSeries'.format(namespace)):
            raiz.find('{}mRID'.format(namespace)).text = datosXML.mRID_Timeseries+str(i)

            i+=1


      tree.write(path_output)
   except Exception as e:
      raise SystemError('Error al escribir : {}'.format(e))

def create_XML_CapDoc(path_output, info_xml, acept=True):
   """

   :param path_input:
   :param path_output:
   :param info_xml:
   :type info_xml: InfoXML
   :param acept:
   :return:
   """
   try:
      datosXML = ParamXML_CapDoc()
      root = ET.Element("Capacity_MarketDocument", datosXML.atribute_capDoc)
      # root.set('xsi:schemaLocation','urn:iec62325.351:tc57wg16:451-3:capacitydocument:8:0 iec62325-451-3-capacity_v8_0.xsd')
      # root.set('xmlns','urn:iec62325.351:tc57wg16:451-3:capacitydocument:8:0')
      # root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

      mrid = info_xml.fecha_end.strftime(datosXML.mRID_REE)
      __add_element(root=root, tag='mRID', text=mrid, attrib={})
      __add_element(root=root, tag='revisionNumber', text='1', attrib={})
      __add_element(root=root, tag='type', text=datosXML.type_doc, attrib={})
      __add_element(root=root, tag='process.processType', text=datosXML.processType, attrib={})


      __add_element(root=root, tag='sender_MarketParticipant.mRID', text=datosXML.MarketParticipant_mRID_SO, attrib={'codingScheme':datosXML.codingScheme})
      __add_element(root=root, tag='sender_MarketParticipant.marketRole.type', text=datosXML.MarketParticipant_Role_SO, attrib={})
      __add_element(root=root, tag='receiver_MarketParticipant.mRID', text=datosXML.MarketParticipant_mRID_CC, attrib={'codingScheme':datosXML.codingScheme})
      __add_element(root=root, tag='receiver_MarketParticipant.marketRole.type', text=datosXML.MarketParticipant_Role_CC, attrib={})


      fecha_create_zulu=get_hora_zulu()
      __add_element(root=root, tag='createdDateTime', text=fecha_create_zulu, attrib={})

      doc_estus_value = datosXML.docStatus_Acept if acept else datosXML.docStatus_Reject
      ele =__add_element(root=root, tag='docStatus', text=None, attrib={})
      __add_subElment(parent =ele, tag = 'value', text=doc_estus_value, attrib={})

      __add_element(root=root, tag='received_MarketDocument.mRID', text=info_xml.mRID, attrib={})
      __add_element(root=root, tag='received_MarketDocument.revisionNumber', text=info_xml.revisionNumber, attrib={})

      ele = __add_element(root=root, tag='period.timeInterval', text=None, attrib={})
      __add_subElment(parent=ele, tag='start', text=info_xml.periodo_star, attrib={})
      __add_subElment(parent=ele, tag='end', text=info_xml.periodo_end, attrib={})

      __add_element(root=root, tag='domain.mRID', text=datosXML.domain_mRID, attrib={'codingScheme':datosXML.codingScheme})

      serie=1
      for flujo in [info_xml.fr_es, info_xml.es_fr, info_xml.pt_es, info_xml.es_pt]:  # type: InfoSentidos
         timeSerie=__add_element(root=root, tag='TimeSeries', text=None, attrib={})
         __add_subElment(parent=timeSerie, tag='mRID', text=datosXML.TimeSeries_mRID+'-'+str(serie), attrib={})
         __add_subElment(parent=timeSerie, tag='businessType', text=datosXML.businessType, attrib={})
         __add_subElment(parent=timeSerie, tag='product', text=datosXML.product, attrib={})
         __add_subElment(parent=timeSerie, tag='in_Domain.mRID', text=flujo.domain_in['mRID'], attrib={'codingScheme':datosXML.codingScheme})
         __add_subElment(parent=timeSerie, tag='out_Domain.mRID', text=flujo.domain_out['mRID'],attrib={'codingScheme': datosXML.codingScheme})
         __add_subElment(parent=timeSerie, tag='measure_Unit.name', text=datosXML.measure_Unit,attrib={})
         __add_subElment(parent=timeSerie, tag='curveType', text=datosXML.codingScheme, attrib={})
         period = __add_subElment(parent=timeSerie, tag='Period', text=None, attrib={})
         interval=__add_subElment(parent=period, tag='timeInterval', text=None, attrib={})
         __add_subElment(parent=interval, tag='start', text=info_xml.periodo_star, attrib={})
         __add_subElment(parent=interval, tag='end', text=info_xml.periodo_end, attrib={})
         __add_subElment(parent=period, tag='resolution', text=datosXML.resolution, attrib={})

         for hora in flujo.info_hora:  # type: InfoInterHora
            if hora.potencia != None:
               hora_labe=hora.hora+1
               point=__add_subElment(parent=period, tag='Point', text=None, attrib={})
               __add_subElment(parent=point, tag='position', text=str(hora_labe), attrib={})
               __add_subElment(parent=point, tag='quantity', text=str(int(hora.potencia)), attrib={})

               if hora.aceptada == False:
                  reason=__add_subElment(parent=point, tag='Reason', text=None, attrib={})
                  __add_subElment(parent=reason, tag='code', text=datosXML.reason_code_CapDoc, attrib={})
                  __add_subElment(parent=reason, tag='text', text=datosXML.reason_text_CapDoc, attrib={})

         serie+=1




      __save_xml(path_output = path_output, root=root)


      # tree = ET.ElementTree(root)
      # with open(path_output, "w") as fh:
      #    tree.write(fh)



   except Exception as e:
      raise SystemError('Error create_XML_CapDoc: {}'.format(e))

def create_XML_CNE(path_output, info_xml):
   """

   :param path_input:
   :param path_output:
   :param info_xml:
   :type info_xml: InfoXML
   :param acept:
   :return:
   """
   try:
      datosXML = ParamXML_CapDoc()
      root = ET.Element("CriticalNetworkElement_MarketDocument", datosXML.atribute_CNE)
      # root.set('xsi:schemaLocation','urn:iec62325.351:tc57wg16:451-3:capacitydocument:8:0 iec62325-451-3-capacity_v8_0.xsd')
      # root.set('xmlns','urn:iec62325.351:tc57wg16:451-3:capacitydocument:8:0')
      # root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')

      mrid = info_xml.fecha_end.strftime(datosXML.mRID_REE_CNE)
      __add_element(root=root, tag='mRID', text=mrid, attrib={})
      __add_element(root=root, tag='revisionNumber', text='1', attrib={})
      __add_element(root=root, tag='type', text=datosXML.type_doc_CNE, attrib={})
      __add_element(root=root, tag='process.processType', text=datosXML.processType, attrib={})


      __add_element(root=root, tag='sender_MarketParticipant.mRID', text=datosXML.MarketParticipant_mRID_SO, attrib={'codingScheme':datosXML.codingScheme})
      __add_element(root=root, tag='sender_MarketParticipant.marketRole.type', text=datosXML.MarketParticipant_Role_SO, attrib={})
      __add_element(root=root, tag='receiver_MarketParticipant.mRID', text=datosXML.MarketParticipant_mRID_CC, attrib={'codingScheme':datosXML.codingScheme})
      __add_element(root=root, tag='receiver_MarketParticipant.marketRole.type', text=datosXML.MarketParticipant_Role_CC, attrib={})


      fecha_create_zulu=get_hora_zulu()
      __add_element(root=root, tag='createdDateTime', text=fecha_create_zulu, attrib={})

      ele =__add_element(root=root, tag='docStatus', text=None, attrib={})
      __add_subElment(parent =ele, tag = 'value', text=datosXML.docStatus_Reject, attrib={})

      ele = __add_element(root=root, tag='Received_MarketDocument', text=None, attrib={})
      __add_subElment(parent=ele, tag='mRID', text=info_xml.mRID, attrib={})
      __add_subElment(parent=ele, tag='revisionNumber', text=info_xml.revisionNumber, attrib={})

      ele = __add_element(root=root, tag='time_Period.timeInterval', text=None, attrib={})
      __add_subElment(parent=ele, tag='start', text=info_xml.periodo_star, attrib={})
      __add_subElment(parent=ele, tag='end', text=info_xml.periodo_end, attrib={})

      __add_element(root=root, tag='domain.mRID', text=datosXML.domain_mRID, attrib={'codingScheme':datosXML.codingScheme})

      serie=1
      for flujo in [info_xml.fr_es, info_xml.es_fr, info_xml.pt_es, info_xml.es_pt]:  # type: InfoSentidos
         modificado= filter(lambda x:  x.aceptada == False, flujo.info_hora).__len__()>0
         if modificado == False:
            continue

         timeSerie=__add_element(root=root, tag='TimeSeries', text=None, attrib={})
         __add_subElment(parent=timeSerie, tag='mRID', text=datosXML.TimeSeries_mRID + '-' + str(serie), attrib={})
         __add_subElment(parent=timeSerie, tag='businessType', text=datosXML.businessType_CNE_TimeSerie, attrib={})
         __add_subElment(parent=timeSerie, tag='in_Domain.mRID', text=flujo.domain_in['mRID'], attrib={'codingScheme':datosXML.codingScheme})
         __add_subElment(parent=timeSerie, tag='out_Domain.mRID', text=flujo.domain_out['mRID'],attrib={'codingScheme': datosXML.codingScheme})
         __add_subElment(parent=timeSerie, tag='curveType', text=datosXML.curveType_CNE, attrib={})
         period = __add_subElment(parent=timeSerie, tag='Period', text=None, attrib={})
         interval=__add_subElment(parent=period, tag='timeInterval', text=None, attrib={})
         __add_subElment(parent=interval, tag='start', text=info_xml.periodo_star, attrib={})
         __add_subElment(parent=interval, tag='end', text=info_xml.periodo_end, attrib={})
         __add_subElment(parent=period, tag='resolution', text=datosXML.resolution, attrib={})

         constrain=1
         for hora in flujo.info_hora:  # type: InfoInterHora
            if hora.aceptada == False:
               hora_labe=hora.hora+1
               if hora.cont_mRid==None  and  hora.mont_mRid==None:
                  mrid_cont=datosXML.mRID_Constraint_Nan
               elif hora.cont_mRid!=None  and  hora.mont_mRid==None:
                  mrid_cont = datosXML.mRID_Constraint_Co
               elif hora.cont_mRid==None  and  hora.mont_mRid!=None:
                  mrid_cont = datosXML.mRID_Constraint_Mon
               else:
                  mrid_cont = datosXML.mRID_Constraint_CoMon
               if constrain<10:
                  mrid_cont = mrid_cont+'00'+str(constrain)
               else:
                  mrid_cont = mrid_cont + '0' + str(constrain)

               point=__add_subElment(parent=period, tag='Point', text=None, attrib={})
               __add_subElment(parent=point, tag='position', text=str(hora_labe), attrib={})
               constraint=__add_subElment(parent=point, tag='Constraint_Series', text=None, attrib={})
               __add_subElment(parent=constraint, tag='mRID', text=mrid_cont, attrib={})
               __add_subElment(parent=constraint, tag='businessType', text=datosXML.businessType_CNE_TimeSerie, attrib={})
               if hora.cont_mRid != None:
                  Contingency_Series=__add_subElment(parent=constraint, tag='Contingency_Series', text=None,attrib={})
                  __add_subElment(parent=Contingency_Series, tag='mRID', text=hora.cont_mRid,attrib={})
                  __add_subElment(parent=Contingency_Series, tag='name', text=hora.cont_name, attrib={})
               if hora.mont_mRid != None:
                  Monitored_RegisteredResource = __add_subElment(parent=constraint, tag='Monitored_RegisteredResource', text=None, attrib={})
                  __add_subElment(parent=Monitored_RegisteredResource, tag='mRID', text=hora.mont_mRid, attrib={'codingScheme': datosXML.codingScheme})
                  __add_subElment(parent=Monitored_RegisteredResource, tag='name', text=hora.mont_name, attrib={})
                  __add_subElment(parent=Monitored_RegisteredResource, tag='in_Domain.mRID', text=hora.mont_domainIN, attrib={'codingScheme': datosXML.codingScheme})
                  __add_subElment(parent=Monitored_RegisteredResource, tag='out_Domain.mRID', text=hora.mont_domainOUT, attrib={'codingScheme': datosXML.codingScheme})



               Reason = __add_subElment(parent=constraint, tag='Reason', text=None,attrib={})
               __add_subElment(parent=Reason, tag='code', text=hora.rea_code, attrib={})

               reason_text = hora.rea_coment if hora.rea_text =='' else hora.rea_text
               reason_text_ele = __add_subElment(parent=Reason, tag='text', text=reason_text, attrib={})

               # reason_text_ele= None
               # for x in reason_text.split('\n'):
               #    if reason_text_ele == None:
               #       reason_text_ele=__add_subElment(parent=Reason, tag='text', text=x, attrib={})
               #    else:
               #       text= reason_text_ele.text
               #       reason_text_ele.text +=text+ '\n'+x

               expla_text = hora.explat_coment if hora.explat_text == '' else hora.explat_text
               Expla = __add_subElment(parent=constraint, tag='Reason', text=None,attrib={})
               __add_subElment(parent=Expla, tag='code', text=hora.explat_code, attrib={})
               __add_subElment(parent=Expla, tag='text', text=expla_text, attrib={})

         serie+=1



      __save_xml(path_output = path_output, root=root)


      # tree = ET.ElementTree(root)
      # with open(path_output, "w") as fh:
      #    tree.write(fh)



   except Exception as e:
      raise SystemError('Error create_XML_CapDoc: {}'.format(e))

def get_hora_zulu(date=datetime.datetime.now()):

   try:
      local = pytz.timezone("Europe/Madrid")
      local_dt = local.localize(date, is_dst=None)
      utc_dt = local_dt.astimezone(pytz.utc)

      datime_zulu = utc_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

      return datime_zulu
   except Exception as e:
      raise SystemError('Error al get_hora_zulu :{}'.format(e))


def __add_element(root,tag,text=None,attrib={}):
   try:
      ele = ET.Element(tag=tag, attrib =attrib)
      if text != None:
         ele.text = text
      root.append(element=ele)

      return ele
   except Exception as e:
      raise  SystemError('Error al add_element :{}. {}'.format(tag,e))

def __add_subElment(parent, tag,text=None, attrib={}):
   try:
      ele = ET.SubElement(parent=parent,tag=tag, attrib =attrib)
      if text != None:
         ele.text = text
      #root.append(element=ele)

      return ele
   except Exception as e:
      raise  SystemError('Error al __add_subElment :{}. {}'.format(tag,e))

def __save_xml(path_output,root):
   try:
      xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
      with open(path_output, "w") as f:
         f.write(xmlstr)
   except Exception as e:
      raise SystemError('Error al __save_xml :{}'.format(e))
