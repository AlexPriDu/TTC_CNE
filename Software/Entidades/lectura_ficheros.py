import datetime
from Software.Entidades.entidades import Rutas
import os
import pandas as pd


def lectura_excel_crack():
   try:
      ruta_excel=Rutas().ruta_excel_crack

      columns_mon=['BORDER','NPSSE_FROM','NPSSE_TO','CKT','LOCATION','ELEMENT','DESCRIPTION','SENSE','PATL','UNIT']
      columns_co_dict=['mRID CO Dict','name CO Dict','NPSSE_FROM','NPSSE_TO','CKT','LOCATION','ELEMENT']

      df_excel_MON = pd.read_excel(ruta_excel, sheet_name='MON', header=2,encoding='utf8')
      df_excel_MON = df_excel_MON[columns_mon]
      df_excel_MON=df_excel_MON.drop_duplicates(['NPSSE_FROM','NPSSE_TO','CKT'], keep='first')

      df_excel_co_dict = pd.read_excel(ruta_excel, sheet_name='CO_DICT', header=0,encoding='utf8')
      df_excel_co_dict=df_excel_co_dict[columns_co_dict]
      df_excel_co_dict = df_excel_co_dict.drop_duplicates(['mRID CO Dict'], keep='first')

      return  df_excel_MON,df_excel_co_dict
   except Exception as e:
      raise SystemError ('Error en la lectura_excel_crack: {}'.format(e))





