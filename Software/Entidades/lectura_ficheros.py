import datetime
from Software.Entidades.entidades import Rutas
import os
import pandas as pd
import re
import cStringIO



def lectura_excel_crack():
   def __get_branch_original(row):

      # if row['indicator']== 'both':
      #    if (row['Raw Bus1']+row['Raw Bus2']==row['bus_from']+row['bus_X']) and (row['Raw Bus1']==row['bus_X']):
      #       row['Raw Bus1'] = row['bus_to'] #El Bus1 del IdReport es el  NudoX. Debe ser sustotuido por el nudo origial.
      #       # EN esta caso el nudo origiganl es el to: row['Raw Bus1']+row['Raw Bus2']==row['bus_from']+row['bus_X']
      #    elif (row['Raw Bus1']+row['Raw Bus2']==row['bus_from']+row['bus_X']) and (row['Raw Bus2']==row['bus_X']):
      #       row['Raw Bus2'] = row['bus_to']
      #    elif (row['Raw Bus1']+row['Raw Bus2']==row['bus_to']+row['bus_X']) and (row['Raw Bus2']==row['bus_X']):
      #       row['Raw Bus2'] = row['bus_from']
      #    elif (row['Raw Bus1']+row['Raw Bus2']==row['bus_to']+row['bus_X']) and (row['Raw Bus1']==row['bus_X']):
      #       row['Raw Bus1'] = row['bus_to']

      if row['indicator'] == 'both':
         if (row['Raw Bus1'] == row['bus_X']) and (row['Raw Bus2']==row['bus_to']):
            #  En este caso el bus1 del IdReport es el nudoX. Hay que cambairlo por el origial. Sinedo el roginal el bus_form -->(row['Raw Bus2']==row['bus_to'])
            row['Raw Bus1'] = row['bus_from']
         elif (row['Raw Bus1'] == row['bus_X']) and (row['Raw Bus2']==row['bus_from']):
            row['Raw Bus1'] = row['bus_to']
         elif (row['Raw Bus2'] == row['bus_X']) and (row['Raw Bus1']==row['bus_from']):
            row['Raw Bus2'] = row['bus_to']
         elif (row['Raw Bus2'] == row['bus_X']) and (row['Raw Bus1']==row['bus_to']):
            row['Raw Bus2'] = row['bus_from']

         row['bus_X_add'] = row['bus_X']

      return  row

   try:
      ruta_excel=Rutas().ruta_excel_crack

      if not os.path.exists(ruta_excel):
         raise SystemError('No existe el excel del crack en la ruta: {}'.format(ruta_excel))

      columns_mon=['BORDER','NPSSE_FROM','NPSSE_TO','CKT','LOCATION','ELEMENT','DESCRIPTION','SENSE','PATL','UNIT']
      columns_co_dict=['mRID CO Dict','name CO Dict','NPSSE_FROM','NPSSE_TO','CKT','LOCATION','ELEMENT']

      df_excel_MON = pd.read_excel(ruta_excel, sheet_name='MON', header=2,encoding='utf8')
      df_excel_MON = df_excel_MON[columns_mon]
      df_excel_MON=df_excel_MON.drop_duplicates(['NPSSE_FROM','NPSSE_TO','CKT'], keep='first')
      df_excel_MON['NPSSE_FROM']= df_excel_MON['NPSSE_FROM'].astype(int)
      df_excel_MON['NPSSE_TO'] = df_excel_MON['NPSSE_TO'].astype(int)
      df_excel_MON['CKT'] = df_excel_MON['CKT'].astype(str)

      df_nudos_X = read_nudosX(ruta_excel=Rutas().ruta_dic_nudox)
      df_nudos_X['ckt'] = df_nudos_X['ckt'].str.strip()

      datos_idReport=read_idReport(ruta_excel=Rutas().ruta_idReport)
      df_idReport_lineas=datos_idReport['df_branch']
      df_idReport_trafo = datos_idReport['df_trafo']


      columns_Mon = list(df_excel_MON.columns.values)

      df_idReport_lineas['Raw Bus1']=df_idReport_lineas['Raw Bus1'].astype(int)
      df_idReport_lineas['Raw Bus2'] = df_idReport_lineas['Raw Bus2'].astype(int)
      df_idReport_lineas['Branch ID'] = df_idReport_lineas['Branch ID'].astype(str)
      df_idReport_lineas['Branch ID']= df_idReport_lineas['Branch ID'].str.strip()
      df_idReport_lineas['Raw Bus1_sep'] = df_idReport_lineas['Raw Bus1']-40000
      df_idReport_lineas['Raw Bus2_sep'] = df_idReport_lineas['Raw Bus2'] - 40000

      columns_IdReport = list(df_idReport_lineas.columns.values)

      df_idReport_trafo['Raw Bus1'] = df_idReport_trafo['Raw Bus1'].astype(int)
      df_idReport_trafo['Raw Bus2'] = df_idReport_trafo['Raw Bus2'].astype(int)
      df_idReport_trafo['Transformer ID'] = df_idReport_trafo['Transformer ID'].astype(str)
      df_idReport_trafo['Transformer ID'] = df_idReport_trafo['Transformer ID'].str.strip()
      df_idReport_trafo['Raw Bus1_sep'] = df_idReport_trafo['Raw Bus1']-40000
      df_idReport_trafo['Raw Bus2_sep'] = df_idReport_trafo['Raw Bus2']-40000

      df_nudos_X['ckt']=df_nudos_X['ckt'].astype(str)

      #Comparoel IDrEPORT CONTRA EN FICHERO DE NUDOS x
      #Las lineas de interconexion oroginales se parten mediante el nudo X:
      #Es dicr la linea del MON: 18105-18195-1--> Sera en el ID Report: 13996-18195-1
      #Donde en el fichero Nudox: 18105 18195 1 XLL_BA11  13996
      #POr lo que tengo que cambiar todos las lineas con nudos X del IdReport por susu originales: IdReport: 13996-18195-1 -->
      columns_IdReport.append('bus_X_add')
      df_idReport_lineas['bus_X_add']=None

      df_idReport_lineas = pd.merge(df_idReport_lineas, df_nudos_X, left_on=['Raw Bus1','Raw Bus2','Branch ID'], right_on=['bus_from','bus_X','ckt'],
                            how='outer', suffixes=('', '_2'), indicator='indicator')
      df_idReport_lineas=df_idReport_lineas.apply(lambda row: __get_branch_original(row), axis=1)
      df_idReport_lineas = df_idReport_lineas.loc[lambda df: (df['indicator'] == 'both') | (df['indicator'] == 'left_only'), :]
      df_idReport_lineas = df_idReport_lineas[columns_IdReport]

      df_idReport_lineas = pd.merge(df_idReport_lineas, df_nudos_X, left_on=['Raw Bus1', 'Raw Bus2', 'Branch ID'],
                                      right_on=['bus_X', 'bus_from', 'ckt'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')

      df_idReport_lineas = df_idReport_lineas.apply(lambda row: __get_branch_original(row), axis=1)
      df_idReport_lineas = df_idReport_lineas.loc[
                           lambda df: (df['indicator'] == 'both') | (df['indicator'] == 'left_only'), :]
      df_idReport_lineas = df_idReport_lineas[columns_IdReport]
      df_idReport_lineas = pd.merge(df_idReport_lineas, df_nudos_X, left_on=['Raw Bus1', 'Raw Bus2', 'Branch ID'],
                                      right_on=['bus_to', 'bus_X', 'ckt'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')

      df_idReport_lineas = df_idReport_lineas.apply(lambda row: __get_branch_original(row), axis=1)
      df_idReport_lineas = df_idReport_lineas.loc[ lambda df: (df['indicator'] == 'both') | (df['indicator'] == 'left_only'), :]
      df_idReport_lineas = df_idReport_lineas[columns_IdReport]

      df_idReport_lineas = pd.merge(df_idReport_lineas, df_nudos_X, left_on=['Raw Bus1', 'Raw Bus2', 'Branch ID'],
                                      right_on=['bus_X', 'bus_to', 'ckt'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')
      df_idReport_lineas = df_idReport_lineas.apply(lambda row: __get_branch_original(row), axis=1)
      df_idReport_lineas = df_idReport_lineas.loc[lambda df: (df['indicator'] == 'both') | (df['indicator'] == 'left_only'), :]
      df_idReport_lineas = df_idReport_lineas[columns_IdReport]


      df_excel_MON_linea = df_excel_MON.loc[lambda df: (df['ELEMENT'] == 'LINEA'), :]
      df_excel_MON_linea_1 = pd.merge(df_idReport_lineas, df_excel_MON_linea, left_on=['Raw Bus1', 'Raw Bus2', 'Branch ID'],
                                    right_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                    how='outer', suffixes=('', '_2'), indicator='indicator')
      df_excel_MON_linea_1 = df_excel_MON_linea_1.loc[lambda df: (df['indicator'] == 'both'), :]


      df_excel_MON_linea_2 = pd.merge(df_idReport_lineas, df_excel_MON_linea,
                                      left_on=['Raw Bus2', 'Raw Bus1', 'Branch ID'],
                                      right_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')
      df_excel_MON_linea_2 = df_excel_MON_linea_2.loc[lambda df: (df['indicator'] == 'both'), :]


      df_excel_MON_linea_3 = pd.merge(df_idReport_lineas, df_excel_MON_linea,
                                      left_on=['Raw Bus1_sep', 'Raw Bus2', 'Branch ID'],
                                      right_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')
      df_excel_MON_linea_3 = df_excel_MON_linea_3.loc[lambda df: (df['indicator'] == 'both'), :]

      df_excel_MON_linea_4 = pd.merge(df_idReport_lineas, df_excel_MON_linea,
                                      left_on=['Raw Bus2', 'Raw Bus1_sep', 'Branch ID'],
                                      right_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')
      df_excel_MON_linea_4 = df_excel_MON_linea_4.loc[lambda df: (df['indicator'] == 'both'), :]

      df_excel_MON_linea_5 = pd.merge(df_idReport_lineas, df_excel_MON_linea,
                                      left_on=['Raw Bus1', 'Raw Bus2_sep', 'Branch ID'],
                                      right_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')
      df_excel_MON_linea_5 = df_excel_MON_linea_5.loc[lambda df: (df['indicator'] == 'both'), :]

      df_excel_MON_linea_6 = pd.merge(df_idReport_lineas, df_excel_MON_linea,
                                      left_on=['Raw Bus2_sep', 'Raw Bus1', 'Branch ID'],
                                      right_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')
      df_excel_MON_linea_6 = df_excel_MON_linea_6.loc[lambda df: (df['indicator'] == 'both'), :]



      df_excel_MON_lineas = pd.concat([df_excel_MON_linea_1, df_excel_MON_linea_2,df_excel_MON_linea_3,df_excel_MON_linea_4,df_excel_MON_linea_5,df_excel_MON_linea_6], ignore_index=True)




      df_excel_MON_trafo = df_excel_MON.loc[lambda df: (df['ELEMENT'] == 'TRAFO'), :]
      df_excel_MON_trafo_1 = pd.merge(df_idReport_trafo, df_excel_MON_trafo,
                                      left_on=['Raw Bus1', 'Raw Bus2', 'Transformer ID'],
                                      right_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')

      df_excel_MON_trafo_1 = df_excel_MON_trafo_1.loc[lambda df: (df['indicator'] == 'both'), :]


      df_excel_MON_trafo_2 = pd.merge(df_idReport_trafo, df_excel_MON_trafo,
                                      left_on=['Raw Bus2', 'Raw Bus1', 'Transformer ID'],
                                      right_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')
      df_excel_MON_trafo_2 = df_excel_MON_trafo_2.loc[lambda df: (df['indicator'] == 'both'), :]

      df_excel_MON_trafo_3 = pd.merge(df_idReport_trafo, df_excel_MON_trafo,
                                      left_on=['Raw Bus1_sep', 'Raw Bus2', 'Transformer ID'],
                                      right_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')

      df_excel_MON_trafo_3 = df_excel_MON_trafo_3.loc[lambda df: (df['indicator'] == 'both'), :]

      df_excel_MON_trafo_4 = pd.merge(df_idReport_trafo, df_excel_MON_trafo,
                                      left_on=['Raw Bus2', 'Raw Bus1_sep', 'Transformer ID'],
                                      right_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')

      df_excel_MON_trafo_4 = df_excel_MON_trafo_4.loc[lambda df: (df['indicator'] == 'both'), :]

      df_excel_MON_trafo_5 = pd.merge(df_idReport_trafo, df_excel_MON_trafo,
                                      left_on=['Raw Bus1', 'Raw Bus2_sep', 'Transformer ID'],
                                      right_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')

      df_excel_MON_trafo_5 = df_excel_MON_trafo_5.loc[lambda df: (df['indicator'] == 'both'), :]

      df_excel_MON_trafo_6 = pd.merge(df_idReport_trafo, df_excel_MON_trafo,
                                      left_on=['Raw Bus2_sep', 'Raw Bus1', 'Transformer ID'],
                                      right_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')

      df_excel_MON_trafo_6 = df_excel_MON_trafo_6.loc[lambda df: (df['indicator'] == 'both'), :]

      df_excel_MON_trafos = pd.concat([df_excel_MON_trafo_1, df_excel_MON_trafo_2, df_excel_MON_trafo_3,df_excel_MON_trafo_4,df_excel_MON_trafo_5,df_excel_MON_trafo_6], ignore_index=True)

      df_excel_MON_des=pd.concat([df_excel_MON_trafos, df_excel_MON_lineas], ignore_index=True)
      columns_Mon.append('Cim ID')
      df_excel_MON_des = df_excel_MON_des[columns_Mon]

      compra_mon= pd.merge(df_excel_MON_des, df_excel_MON,
                                      left_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                      right_on=['NPSSE_FROM', 'NPSSE_TO', 'CKT'],
                                      how='outer', suffixes=('', '_2'), indicator='indicator')
      df_mon_error= compra_mon.loc[lambda df: (df['indicator'] != 'both'), :]


      df_excel_co_dict = pd.read_excel(ruta_excel, sheet_name='CO_DICT', header=0,encoding='utf8')
      df_excel_co_dict=df_excel_co_dict[columns_co_dict]
      df_excel_co_dict = df_excel_co_dict.drop_duplicates(['mRID CO Dict'], keep='first')

      return  df_excel_MON_des,df_excel_co_dict,df_mon_error
   except Exception as e:
      raise SystemError ('Error en la lectura_excel_crack: {}'.format(e))


def read_idReport(ruta_excel = None):
   try:

      if not os.path.exists(ruta_excel):
         raise SystemError('No existe el excel del idReport en la ruta: {}'.format(ruta_excel))


      patron_bus = re.compile('#BUS', re.I | re.MULTILINE)
      patron_load = re.compile('#LOAD',re.I | re.MULTILINE)
      patron_fixed = re.compile('#FIXEDSHUNT', re.I | re.MULTILINE)
      patron_gen = re.compile('#GENERATOR', re.I | re.MULTILINE)
      patron_branch = re.compile('#BRANCH', re.I | re.MULTILINE)
      patron_trafo = re.compile('#TRANSFORMERS', re.I | re.MULTILINE)
      patron_sw = re.compile('#SWITCHED SHUNT', re.I | re.MULTILINE)
      patron_area= re.compile('#AREA', re.I | re.MULTILINE)

      ifile = open(ruta_excel, 'r')
      linea = ifile.read()
      ifile.close()

      matcher_bus = patron_bus.search(linea)
      matcher_load=patron_load.search(linea)
      matcher_fixed = patron_fixed.search(linea)
      matcher_gen = patron_gen.search(linea)
      matcher_branch = patron_branch.search(linea)
      matcher_trafo = patron_trafo.search(linea)
      matcher_sw = patron_sw.search(linea)
      matcher_area = patron_area.search(linea)

      if matcher_bus == None:
         raise SystemError('No se ha encontrado en patron de BUS')
      if matcher_load == None:
         raise SystemError('No se ha encontrado en patron de LOAD')
      if matcher_fixed == None:
         raise SystemError('No se ha encontrado en patron de FIXEDSHUNT')
      if matcher_gen == None:
         raise SystemError('No se ha encontrado en patron de GENERATOR')
      if matcher_branch == None:
         raise SystemError('No se ha encontrado en patron de BRANCH')
      if matcher_trafo == None:
         raise SystemError('No se ha encontrado en patron de TRANSFORMERS')
      if matcher_sw == None:
         raise SystemError('No se ha encontrado en patron de SWITCHED SHUNT')
      if matcher_area == None:
         raise SystemError('No se ha encontrado en patron de AREA')

      TEXT_BUS =linea[matcher_bus.end(): matcher_load.start()-1]
      TEXT_LOAD = linea[matcher_load.end(): matcher_fixed.start()-1]
      TEXT_FIXED = linea[matcher_fixed.end():matcher_gen.start()-1]
      TEXT_GEN = linea[matcher_gen.end():matcher_branch.start()-1]
      TEXT_BRANCH = linea[matcher_branch.end():matcher_trafo.start()-1]
      TEXT_TRAFO = linea[matcher_trafo.end():matcher_area.start() - 1]
      TEXT_AREA = linea[matcher_area.end():matcher_sw.start()-1]
      TEXT_SW = linea[matcher_sw.end():]

      df_buses = pd.read_csv(cStringIO.StringIO(TEXT_BUS),sep="," )
      df_load = pd.read_csv(cStringIO.StringIO(TEXT_LOAD), sep=",")
      df_fixed = pd.read_csv(cStringIO.StringIO(TEXT_FIXED), sep=",")
      df_gen = pd.read_csv(cStringIO.StringIO(TEXT_GEN), sep=",")
      df_branch = pd.read_csv(cStringIO.StringIO(TEXT_BRANCH), sep=",")
      df_trafo = pd.read_csv(cStringIO.StringIO(TEXT_TRAFO), sep=",")
      df_area = pd.read_csv(cStringIO.StringIO(TEXT_AREA), sep=",")
      df_sw = pd.read_csv(cStringIO.StringIO(TEXT_SW), sep=",")




      return {'df_buses':df_buses,'df_load':df_load,'df_fixed':df_fixed,'df_gen':df_gen,
              'df_branch':df_branch,'df_trafo':df_trafo,'df_area':df_area,'df_sw':df_sw}

   except Exception as e:
      raise SystemError('Error al leer el fichero IdReport: {}'.format(e))

def read_nudosX(ruta_excel=None):

   if not os.path.exists(ruta_excel):
      raise SystemError('No existe el excel del NudosX en la ruta: {}'.format(ruta_excel))

   ifile = open(ruta_excel, 'r')
   linea = ifile.readline()
   list_datos=[]

   while True:
      datos=linea.split()
      list_datos.append({'bus_from':int(datos[0].strip()),'bus_to':int(datos[1].strip()),'ckt':datos[2].strip(),'name':datos[3],'bus_X':int(datos[4].strip())})
      linea = ifile.readline()
      if linea =='':break

   ifile.close()



   df = pd.DataFrame(list_datos)

   return df


def get_mRID_by_PSEEId(bus_i, bus_j, ckt, ruta_idReport, ruta_nudosX, bus_k=0, trafo = False):
   def __get_branch_original(row):

      if row['indicator'] == 'both':
         if (row['Raw Bus1'] == row['bus_X']) and (row['Raw Bus2'] == row['bus_to']):
            #  En este caso el bus1 del IdReport es el nudoX. Hay que cambairlo por el origial. Sinedo el roginal el bus_form -->(row['Raw Bus2']==row['bus_to'])
            row['Raw Bus1'] = row['bus_from']
         elif (row['Raw Bus1'] == row['bus_X']) and (row['Raw Bus2'] == row['bus_from']):
            row['Raw Bus1'] = row['bus_to']
         elif (row['Raw Bus2'] == row['bus_X']) and (row['Raw Bus1'] == row['bus_from']):
            row['Raw Bus2'] = row['bus_to']
         elif (row['Raw Bus2'] == row['bus_X']) and (row['Raw Bus1'] == row['bus_to']):
            row['Raw Bus2'] = row['bus_from']

         row['bus_X_add'] = row['bus_X']

      return row
   try:
      ID = None
      df_nudos_X = read_nudosX(ruta_excel=ruta_nudosX)
      df_nudos_X['ckt'] = df_nudos_X['ckt'].str.strip()

      datos_idReport = read_idReport(ruta_excel=ruta_idReport)
      df_idReport_lineas = datos_idReport['df_branch']
      df_idReport_trafo = datos_idReport['df_trafo']


      df_idReport_lineas['Raw Bus1'] = df_idReport_lineas['Raw Bus1'].astype(int)
      df_idReport_lineas['Raw Bus2'] = df_idReport_lineas['Raw Bus2'].astype(int)
      df_idReport_lineas['Branch ID'] = df_idReport_lineas['Branch ID'].astype(str)
      df_idReport_lineas['Branch ID'] = df_idReport_lineas['Branch ID'].str.strip()
      df_idReport_lineas['Raw Bus1_sep'] = df_idReport_lineas['Raw Bus1'] - 40000
      df_idReport_lineas['Raw Bus2_sep'] = df_idReport_lineas['Raw Bus2'] - 40000

      columns_IdReport = list(df_idReport_lineas.columns.values)

      df_idReport_trafo['Raw Bus1'] = df_idReport_trafo['Raw Bus1'].astype(int)
      df_idReport_trafo['Raw Bus2'] = df_idReport_trafo['Raw Bus2'].astype(int)
      df_idReport_trafo['Transformer ID'] = df_idReport_trafo['Transformer ID'].astype(str)
      df_idReport_trafo['Transformer ID'] = df_idReport_trafo['Transformer ID'].str.strip()
      df_idReport_trafo['Raw Bus1_sep'] = df_idReport_trafo['Raw Bus1'] - 40000
      df_idReport_trafo['Raw Bus2_sep'] = df_idReport_trafo['Raw Bus2'] - 40000

      df_nudos_X['ckt'] = df_nudos_X['ckt'].astype(str)

      # Comparoel IDrEPORT CONTRA EN FICHERO DE NUDOS x
      # Las lineas de interconexion oroginales se parten mediante el nudo X:
      # Es dicr la linea del MON: 18105-18195-1--> Sera en el ID Report: 13996-18195-1
      # Donde en el fichero Nudox: 18105 18195 1 XLL_BA11  13996
      # POr lo que tengo que cambiar todos las lineas con nudos X del IdReport por susu originales: IdReport: 13996-18195-1 -->
      columns_IdReport.append('bus_X_add')
      df_idReport_lineas['bus_X_add'] = None

      df_idReport_lineas = pd.merge(df_idReport_lineas, df_nudos_X, left_on=['Raw Bus1', 'Raw Bus2', 'Branch ID'],
                                    right_on=['bus_from', 'bus_X', 'ckt'],
                                    how='outer', suffixes=('', '_2'), indicator='indicator')
      df_idReport_lineas = df_idReport_lineas.apply(lambda row: __get_branch_original(row), axis=1)
      df_idReport_lineas = df_idReport_lineas.loc[
                           lambda df: (df['indicator'] == 'both') | (df['indicator'] == 'left_only'), :]
      df_idReport_lineas = df_idReport_lineas[columns_IdReport]

      df_idReport_lineas = pd.merge(df_idReport_lineas, df_nudos_X, left_on=['Raw Bus1', 'Raw Bus2', 'Branch ID'],
                                    right_on=['bus_X', 'bus_from', 'ckt'],
                                    how='outer', suffixes=('', '_2'), indicator='indicator')

      df_idReport_lineas = df_idReport_lineas.apply(lambda row: __get_branch_original(row), axis=1)
      df_idReport_lineas = df_idReport_lineas.loc[
                           lambda df: (df['indicator'] == 'both') | (df['indicator'] == 'left_only'), :]
      df_idReport_lineas = df_idReport_lineas[columns_IdReport]
      df_idReport_lineas = pd.merge(df_idReport_lineas, df_nudos_X, left_on=['Raw Bus1', 'Raw Bus2', 'Branch ID'],
                                    right_on=['bus_to', 'bus_X', 'ckt'],
                                    how='outer', suffixes=('', '_2'), indicator='indicator')

      df_idReport_lineas = df_idReport_lineas.apply(lambda row: __get_branch_original(row), axis=1)
      df_idReport_lineas = df_idReport_lineas.loc[
                           lambda df: (df['indicator'] == 'both') | (df['indicator'] == 'left_only'), :]
      df_idReport_lineas = df_idReport_lineas[columns_IdReport]

      df_idReport_lineas = pd.merge(df_idReport_lineas, df_nudos_X, left_on=['Raw Bus1', 'Raw Bus2', 'Branch ID'],
                                    right_on=['bus_X', 'bus_to', 'ckt'],
                                    how='outer', suffixes=('', '_2'), indicator='indicator')
      df_idReport_lineas = df_idReport_lineas.apply(lambda row: __get_branch_original(row), axis=1)
      df_idReport_lineas = df_idReport_lineas.loc[ lambda df: (df['indicator'] == 'both') | (df['indicator'] == 'left_only'), :]
      df_idReport_lineas = df_idReport_lineas[columns_IdReport]

      df = pd.DataFrame()

      if trafo == False:
         df = df_idReport_lineas.loc[lambda df: (((df['Raw Bus1'] == bus_i) & (df['Raw Bus2'] == bus_j)) | (
                  (df['Raw Bus1'] == bus_j) & (df['Raw Bus2'] == bus_i)))
                                                & (df['Branch ID'] == ckt), :]
      elif trafo == True and bus_k == 0:
         df = df_idReport_trafo.loc[lambda df: (((df['Raw Bus1'] == bus_i) & (df['Raw Bus2'] == bus_j))
                                                | ((df['Raw Bus1'] == bus_j) & (df['Raw Bus2'] == bus_i)))
                                               & (df['Transformer ID'] == ckt), :]
      else:
         df = df_idReport_trafo.loc[lambda df: (((df['Raw Bus1'] == bus_i) & (df['Raw Bus2'] == bus_j)  & (df['Raw Bus3'] == bus_k))
                                                | ((df['Raw Bus1'] == bus_j) & (df['Raw Bus2'] == bus_i)) & (df['Raw Bus3'] == bus_k)) & (df['Transformer ID'] == ckt), :]

      if df.empty == False:
         ID = df.iloc[0]['Cim ID']
      else:
         raise SystemError('No se ha encontrado el mRID para el elemento {}-{}-{}'.format(bus_i, bus_j, ckt))

      return ID
   except Exception as e:
      raise SystemError('Error al get_mRID_by_PSEE {}'.format(e))


if __name__ == '__main__':
   get_mRID_by_PSEEId(bus_i=21060, bus_j=1905, ckt='2', ruta_idReport = "C:\Users\GerardoGuerra\Desktop\Nueva carpeta\REE_IdReport.csv",
                      ruta_nudosX= "C:\Users\GerardoGuerra\Desktop\Nueva carpeta\DICCIONARIO_NUDOS_X.txt", bus_k=0, trafo= True)