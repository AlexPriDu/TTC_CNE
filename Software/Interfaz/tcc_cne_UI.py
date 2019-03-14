

from PySide.QtCore import *
from PySide.QtGui import *
import sys
import os

import pandas as pd
import numpy as np
import datetime

from Software.Entidades.lectura_ficheros import lectura_excel_crack
from Software.Entidades.entidades import Rutas, Domain, ColumnsDataFrame, get_reason_explat_codes
from Software.Core.lectura_xml import lectura_SWE_D2_CapDoc_Prop, InfoXML_to_Dataframe


from Software.Interfaz.vistas.MainWindow import Ui_MainWindow

df_mon, df_co_dict = lectura_excel_crack()
list_reason_codes, list_explat_codes =get_reason_explat_codes()

version='1.0'
__appname__ ='TTC_CNE'


def dobleClickable(widget):  # accion doble click con el raton

   class Filter(QObject):
      clicked = Signal()

      def eventFilter(self, obj, event):
         if obj == widget:
            if event.type() == QEvent.MouseButtonDblClick:
               if obj.rect().contains(event.pos()):
                  self.clicked.emit()
                  # The developer can opt for .emit(obj) to get the object within the slot.
                  return True
         return False

   filter = Filter(widget)
   widget.installEventFilter(filter)
   return filter.clicked


class CustomQCompleter(QCompleter):
   def __init__(self, parent=None):
      super(CustomQCompleter, self).__init__(parent)
      self.local_completion_prefix = ""
      self.source_model = None

   def setModel(self, model):
      self.source_model = model
      super(CustomQCompleter, self).setModel(self.source_model)

   def updateModel(self):
      local_completion_prefix = self.local_completion_prefix

      class InnerProxyModel(QSortFilterProxyModel):
         def filterAcceptsRow(self, sourceRow, sourceParent):
            index0 = self.sourceModel().index(sourceRow, 0, sourceParent)
            return local_completion_prefix.lower() in self.sourceModel().data(index0).lower()

      proxy_model = InnerProxyModel()
      proxy_model.setSourceModel(self.source_model)
      super(CustomQCompleter, self).setModel(proxy_model)

   def splitPath(self, path):
      self.local_completion_prefix = path
      self.updateModel()
      return ""

class Main(QMainWindow,Ui_MainWindow):

   def __init__(self, parent= None):
      super(Main, self).__init__(parent)
      self.setupUi(self)
      self.settings = QSettings(QSettings.IniFormat, QSettings.UserScope, "Pcc_UI", "Pcc_UI")

      self.setWindowTitle('TCC CNE {}'.format(version))

      self.fecha =datetime.datetime.now()
      self.fecha=self.fecha.replace(day=07)
      self.columns_df = ColumnsDataFrame.columns



      self.path_xml_capDoc =None
      self.path_xml_capDoc_Re=None
      self.path_xml_capDoc_Acep=None
      self.path_xml_cen_Det=None

      self.df_table_edit=None
      self.df_table_ini = None
      self.df_data_edit=pd.DataFrame(columns=['sentido','hora','valor_new','valor_old'])
      self.df_compare=None
      self.change_table=False


      self.es_fr=ES_FR(ui=self,periodo=self.fecha)
      self.fr_es=FR_ES(ui=self,periodo=self.fecha)
      self.es_pt=ES_PT(ui=self,periodo=self.fecha)
      self.pt_es=PT_ES(ui=self,periodo=self.fecha)

      #self.load_comboBox()
      self.edit_informacion_hora(False)

      fecha=QDateTime(self.fecha)

      self.dateEdit.setDate(fecha.date())

      self.tabWidget.setCurrentIndex(0)

      self.df_mon, self.df_co_dict = lectura_excel_crack()
      self.list_mon = self.df_mon.to_dict('records')
      self.list_co_dict = self.df_co_dict.to_dict('records')


      self.pushButton_EditFecha.setEnabled(True)
      self.pushButton_Save_Fecha.setVisible(False)
      self.dateEdit.setEnabled(False)
      self.pushButton_EditFecha.setVisible(False)
      self.pushButton_EditFecha.clicked.connect(self.edit_fecha)
      self.pushButton_Save_Fecha.clicked.connect(self.save_fecha)

      self.pushButton_EditTable.setVisible(False)
      self.pushButton_GenTable.setVisible(False)
      self.pushButton_SaveTable.setVisible(False)

      self.pushButton_LoadTable.clicked.connect(self.cargar_xml_capdoc)

      self.pushButton_EditTable.clicked.connect(lambda: self.edit_table(True))
      self.pushButton_SaveTable.clicked.connect(self.guardar_table)
      self.pushButton_GenTable.clicked.connect(self.generar_xml_salida)

      self.showMaximized()
      #
      # self.tableView.setMaximumSize(lambda x: self.getQTableWidgetSize(x))

      self.model_resultados = QStandardItemModel(self)
      self.proxy = QSortFilterProxyModel(self)
      self.proxy.setSourceModel(self.model_resultados)


      self.tableView.setModel(self.proxy)
      self.horizontalHeader_resultados = self.tableView.horizontalHeader()
      self.tableView.setSortingEnabled(False)
      self.tableView.setSelectionMode(QAbstractItemView.MultiSelection)
      self.tableView.setAlternatingRowColors(1)
      self.tableView.setEnabled(False)
      self.tableView.setVisible(False)

      dobleClickable(self.tableView).connect(self.tableView.clearSelection)
      # self.connect(self.tableView_Resultados, SIGNAL('doubleclicked(QModelIndex)'), SLOT('dblClickHandler(QModelIndex)'))
      # self.connect(self.tableView_Resultados, SIGNAL("doubleClicked(int)"), self.dblClickHandler)

      self.horizontalHeader_resultados = self.tableView.horizontalHeader()

      # self.columns_df = ['Sentidos', '00-01',
      #            '01-02','02-03', '03-04',
      #            '04-05','05-06', '06-07','07-08', '08-09',
      #            '09-10', '10-11','11-12', '12-13',
      #            '13-14','14-15', '15-16',
      #            '16-17','17-18', '18-19',
      #            '19-20', '20-21','21-22', '22-23','23-24']
      #
      # data={'Sentidos':['FR -> ES','ES -> FR','PT -> ES','ES -> PT'],'00-01':[1223, 34345, 234324,213213], '01-02':[4567, 3455, 23897,23987],
      #       '02-03':[236554, 12323, 123333, 23897], '03-04':[4567, 3455, 23897,23987],
      #       '04-05':[236554, 12323, 123333, 23897],'05-06':[236554, 12323, 123333, 23897],'06-07':[4567, 3455, 23897,23987],
      #       '07-08':[4567, 3455, 23897,23987],'08-09':[4567, 3455, 23897,23987],
      #       '09-10':[4567, 3455, 23897,23987],'10-11':[4567, 3455, 23897,23987],
      #       '11-12':[4567, 3455, 23897,23987], '12-13':[4567, 3455, 23897,23987],'13-14':[4567, 3455, 23897,23987],
      #       '14-15':[4567, 3455, 23897,23987],'15-16':[4567, 3455, 23897,23987],'16-17':[4567, 3455, 23897,23987],
      #       '17-18':[4567, 3455, 23897,23987],'18-19':[4567, 3455, 23897,23987],'19-20':[4567, 3455, 23897,23987],'20-21':[4567, 3455, 23897,23987],
      #       '21-22':[4567, 3455, 23897,23987],'22-23':[4567, 3455, 23897,23987],'23-24':[4567, 3455, 23897,23987]}
      # dataframe=pd.DataFrame(data)
      #
      # self.load_tableWiget(df=dataframe)
      # self.load_tableView(df=dataframe)

      self.tableWidget.setSortingEnabled( False)  # Deshabilito la ordenacion en la tabla de nudo. Da problemas al volver a cargar los nudos
      self.tableWidget.setAlternatingRowColors(True)  # Habilito la elternacia de colores en la tabla de nudos
      self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
      self.tableWidget.setSelectionMode(QTableWidget.NoSelection)



      self.Hide_Console()

   def get_path_fichero_xml(self):
      """

      :param fecha:
      :return:
      """
      try:
         ruta = Rutas()
         name_xml=self.fecha.strftime(ruta.name_xml_capDoc_input)
         self.path_xml_capDoc = os.path.join(ruta.directorio_input_xml_coreso,name_xml)

         name_xml=ruta.name_xml_capDoc_re
         self.path_xml_capDoc_Re = os.path.join(ruta.directorio_input_xml_coreso,name_xml)

         name_xml = ruta.name_xml_capDoc_ac
         self.path_xml_capDoc_Acep = os.path.join(ruta.directorio_input_xml_coreso,name_xml)

         name_xml = ruta.name_xml_cne_de
         self.path_xml_cen_Det = os.path.join(ruta.directorio_input_xml_coreso,name_xml)

      except Exception as e:
         raise SystemError('Error al get_path_fichero_xml :{}'.format(e))

   def load_tableWiget(self,df):
      """

      :param df:
      :type df: pd.DataFrame
      :return:
      """
      self.tableWidget.clear()
      self.tableWidget.clearContents()
      self.tableWidget.setRowCount(0)
      while (self.tableWidget.rowCount() > 0):
         self.tableWidget.removeRow(0)


      # for x in range(0,self.tableWidget.rowCount()+1,1):

      if not df.empty:

         df = df[self.columns_df]
         self.df_table_ini=df
         header = self.tableWidget.horizontalHeader()


         self.tableWidget.setColumnCount(len(df.columns.values))
         #self.tableWidget.setRowCount(count_row)
         #header.setResizeMode(0, QHeaderView.Stretch)





         self.tableWidget.setHorizontalHeaderLabels(list(df.columns.values))

         self.tableWidget.setVerticalHeaderLabels(list(df.index))

         i = 0
         for index, row in df.iterrows():
            pass
            self.tableWidget.insertRow(i)
            j=0
            for coln in row:
               data = QTableWidgetItem(str(coln))
               self.tableWidget.setItem(i, j, data)
               j += 1
            i += 1

         hide_columns=False

         for x in range(0, self.tableWidget.columnCount(), 1):
            columns=self.tableWidget.horizontalHeaderItem(x)
            column_text=columns.text()
            if column_text=='Sentidos':
               continue
            else:
               df_none = self.df_table_ini.loc[self.df_table_ini[str(column_text)].isnull()]

               if len(df_none.index.values) ==  len(self.df_table_ini.index.values):
                  hide_columns=True
                  self.tableWidget.setColumnHidden(x, True)


         for col in range(0,len(list(df)),1):
            if hide_columns== False:
               header.setResizeMode(col, QHeaderView.Stretch)
            else:
               header.setResizeMode(x, QHeaderView.ResizeToContents)


      else:
         raise SystemError('No hay datos que cargar')

   def get_table(self):
      try:
         list_data=[]
         self.df_data_edit = pd.DataFrame(columns=['sentido', 'hora', 'valor_new', 'valor_old'])

         allRows = self.tableWidget.rowCount()
         col_count=self.tableWidget.columnCount()
         for row in xrange(0, allRows):
            index = self.tableWidget.item(row, 0).text()
            df_sentido= self.df_table_ini.loc[self.df_table_ini['Sentidos']==index]
            if df_sentido.empty:
               raise SystemError('Error al obgener la tabla. No se ha podido realiza rel filtrado de df_inicial mendiante el sentido: {}'.format(index))
            else:
               df_sentido=df_sentido.iloc[0]

            sentido=df_sentido['Sentidos']

            h0 = self.tableWidget.item(row, 1).text()
            header = str(self.tableWidget.horizontalHeaderItem(1).text())
            change = self.___add_data_edit(df_sentido = df_sentido, header= header, hora_value=h0, sentido_label= sentido, hora_int=0)
            if change:
               self.tableWidget.item(row, 1).setBackground(QColor(255, 0, 0, 127))


            h1 = self.tableWidget.item(row, 2).text()
            header = str(self.tableWidget.horizontalHeaderItem(2).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h1, sentido_label=sentido, hora_int=1)
            if change:
               self.tableWidget.item(row, 2).setBackground(QColor(255, 0, 0, 127))


            h2 = self.tableWidget.item(row, 3).text()
            header = str(self.tableWidget.horizontalHeaderItem(3).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h2, sentido_label=sentido,
                                  hora_int=2)
            if change:
               self.tableWidget.item(row, 3).setBackground(QColor(255, 0, 0, 127))


            h3 = self.tableWidget.item(row, 4).text()
            header = str(self.tableWidget.horizontalHeaderItem(4).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h3, sentido_label=sentido,hora_int=3)
            if change:
               self.tableWidget.item(row, 4).setBackground(QColor(255, 0, 0, 127))


            h4 = self.tableWidget.item(row, 5).text()
            header = str(self.tableWidget.horizontalHeaderItem(5).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h4, sentido_label=sentido,hora_int=4)
            if change:
               self.tableWidget.item(row, 5).setBackground(QColor(255, 0, 0, 127))

            h5 = self.tableWidget.item(row, 6).text()
            header = str(self.tableWidget.horizontalHeaderItem(6).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h5, sentido_label=sentido,hora_int=5)
            if change:
               self.tableWidget.item(row, 6).setBackground(QColor(255, 0, 0, 127))

            h6 = self.tableWidget.item(row, 7).text()
            header = str(self.tableWidget.horizontalHeaderItem(7).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h6, sentido_label=sentido, hora_int=6)
            if change:
               self.tableWidget.item(row, 7).setBackground(QColor(255, 0, 0, 127))

            h7 = self.tableWidget.item(row, 8).text()
            header = str(self.tableWidget.horizontalHeaderItem(8).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h7, sentido_label=sentido,
                                  hora_int=7)
            if change:
               self.tableWidget.item(row, 8).setBackground(QColor(255, 0, 0, 127))

            h8 = self.tableWidget.item(row, 9).text()
            header = str(self.tableWidget.horizontalHeaderItem(9).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h8, sentido_label=sentido,
                                  hora_int=8)
            if change:
               self.tableWidget.item(row, 9).setBackground(QColor(255, 0, 0, 127))

            h9 = self.tableWidget.item(row, 10).text()
            header = str(self.tableWidget.horizontalHeaderItem(10).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h9, sentido_label=sentido,
                                  hora_int=9)
            if change:
               self.tableWidget.item(row, 10).setBackground(QColor(255, 0, 0, 127))

            h10 = self.tableWidget.item(row, 11).text()
            header = str(self.tableWidget.horizontalHeaderItem(11).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h10, sentido_label=sentido,
                                  hora_int=10)
            if change:
               self.tableWidget.item(row, 11).setBackground(QColor(255, 0, 0, 127))

            h11 = self.tableWidget.item(row, 12).text()
            header = str(self.tableWidget.horizontalHeaderItem(12).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h11, sentido_label=sentido,
                                  hora_int=11)
            if change:
               self.tableWidget.item(row, 12).setBackground(QColor(255, 0, 0, 127))

            h12 = self.tableWidget.item(row, 13).text()
            header = str(self.tableWidget.horizontalHeaderItem(13).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h12, sentido_label=sentido,
                                  hora_int=12)
            if change:
               self.tableWidget.item(row, 13).setBackground(QColor(255, 0, 0, 127))

            h13 = self.tableWidget.item(row, 14).text()
            header = str(self.tableWidget.horizontalHeaderItem(14).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h13, sentido_label=sentido,
                                  hora_int=13)
            if change:
               self.tableWidget.item(row, 14).setBackground(QColor(255, 0, 0, 127))

            h14 = self.tableWidget.item(row, 15).text()
            header = str(self.tableWidget.horizontalHeaderItem(15).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h14, sentido_label=sentido,
                                  hora_int=14)
            if change:
               self.tableWidget.item(row, 10).setBackground(QColor(255, 0, 0, 127))

            h15 = self.tableWidget.item(row, 16).text()
            header = str(self.tableWidget.horizontalHeaderItem(16).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h15, sentido_label=sentido,
                                  hora_int=15)
            if change:
               self.tableWidget.item(row, 16).setBackground(QColor(255, 0, 0, 127))

            h16 = self.tableWidget.item(row, 17).text()
            header = str(self.tableWidget.horizontalHeaderItem(17).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h16, sentido_label=sentido,
                                  hora_int=16)

            if change:
               self.tableWidget.item(row, 17).setBackground(QColor(255, 0, 0, 127))

            h17 = self.tableWidget.item(row, 18).text()
            header = str(self.tableWidget.horizontalHeaderItem(18).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h17, sentido_label=sentido,
                                  hora_int=17)
            if change:
               self.tableWidget.item(row, 18).setBackground(QColor(255, 0, 0, 127))

            h18 = self.tableWidget.item(row, 19).text()
            header = str(self.tableWidget.horizontalHeaderItem(19).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h18, sentido_label=sentido,
                                  hora_int=18)
            if change:
               self.tableWidget.item(row, 19).setBackground(QColor(255, 0, 0, 127))

            h19 = self.tableWidget.item(row, 20).text()
            header = str(self.tableWidget.horizontalHeaderItem(20).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h19, sentido_label=sentido,
                                  hora_int=19)
            if change:
               self.tableWidget.item(row, 20).setBackground(QColor(255, 0, 0, 127))

            h20 = self.tableWidget.item(row, 21).text()
            header = str(self.tableWidget.horizontalHeaderItem(21).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h20, sentido_label=sentido,
                                  hora_int=20)
            if change:
               self.tableWidget.item(row,21).setBackground(QColor(255, 0, 0, 127))


            h21 = self.tableWidget.item(row, 22).text()
            header = str(self.tableWidget.horizontalHeaderItem(22).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h21, sentido_label=sentido,
                                  hora_int=21)
            if change:
               self.tableWidget.item(row, 22).setBackground(QColor(255, 0, 0, 127))

            h22= self.tableWidget.item(row, 23).text()
            header = str(self.tableWidget.horizontalHeaderItem(23).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h22, sentido_label=sentido,
                                  hora_int=22)
            if change:
               self.tableWidget.item(row, 23).setBackground(QColor(255, 0, 0, 127))

            h23 = self.tableWidget.item(row, 24).text()
            header = str(self.tableWidget.horizontalHeaderItem(24).text())
            change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h23, sentido_label=sentido,
                                  hora_int=23)
            if change:
               self.tableWidget.item(row, 24).setBackground(QColor(255, 0, 0, 127))

            if col_count == 26:

               h24 = self.tableWidget.item(row, 25).text()
               change = self.___add_data_edit(df_sentido=df_sentido, header=header, hora_value=h24, sentido_label=sentido,
                                     hora_int=25)
               if change:
                  self.tableWidget.item(row, 10).setBackground(QColor(255, 0, 0, 127))
               data = {'Sentidos': index, '00-01': h0, '01-02': h1,
                       '02-03': h2, '03-04': h3, '04-05': h4, '05-06': h5,'06-07': h6,
                       '07-08': h7, '08-09': h8, '09-10': h9, '10-11': h10,
                       '11-12': h11, '12-13': h12, '13-14': h13, '14-15': h14, '15-16': h15, '16-17': h16,
                       '17-18': h17, '18-19': h18, '19-20': h19, '20-21': h20, '21-22': h21, '22-23': h22,'23-24':h23,'24-25': h24}
            else:
               data = {'Sentidos': index, '00-01': h0, '01-02': h1,
                       '02-03': h2, '03-04': h3, '04-05': h4, '05-06': h5, '06-07': h6,
                       '07-08': h7, '08-09': h8, '09-10': h9, '10-11': h10,
                       '11-12': h11, '12-13': h12, '13-14': h13, '14-15': h14, '15-16': h15, '16-17': h16,
                       '17-18': h17, '18-19': h18, '19-20': h19, '20-21': h20, '21-22': h21, '22-23': h22, '23-24': h23}

            list_data.append(data)

         self.df_table_edit=pd.DataFrame(list_data)

         for x in self.df_table_edit.columns.values:
            try:
               if x =='Sentidos':
                  self.df_table_edit[x]=self.df_table_edit[x].astype(str)
               elif str(self.df_table_edit[x][0]) != str(None) :
                  self.df_table_edit[x] = self.df_table_edit[x].astype(float)
            except Exception as e:
               QMessageBox.warning(self, __appname__, 'Algun dato modificado no es un numero :{}'.format(e))
               self.load_tableWiget(df=self.df_table_ini)
               return False
         self.df_table_edit =  self.df_table_edit[self.columns_df]
         return True
      except Exception as e:
         QMessageBox.warning(self, __appname__, 'Algun dato modificado no es un numero :{}'.format(e))
         self.load_tableWiget(df=self.df_table_ini)
         return False

   def load_tableView(self,df):
      if not df.empty:
         self.model_resultados.setHorizontalHeaderLabels(list(df.columns.values))

         for item, frame in df.iterrows():
            list_data = frame
            # self.model_resultados.invisibleRootItem().appendRow([self.get_QStandardItems(x) for x in list_data])
            self.model_resultados.appendRow([self.get_QStandardItems(str(x)) for x in list_data])
      else:
         self.model_resultados.setHorizontalHeaderLabels(list(df.columns.values))

   def ___add_data_edit(self,df_sentido,header,hora_value,sentido_label, hora_int):

      try:
         change=False
         if str(hora_value) == str(None):
            df_add = pd.DataFrame.from_dict(
               [{'sentido': sentido_label, 'hora': hora_int, 'valor_new': None, 'valor_old': None}])
         elif float(df_sentido[header]) != float(hora_value):
            change = True
            df_add=pd.DataFrame.from_dict([{'sentido': sentido_label, 'hora': hora_int, 'valor_new': df_sentido[header], 'valor_old': float(hora_value)}])
         else:
            df_add = pd.DataFrame.from_dict(
               [{'sentido': sentido_label, 'hora': hora_int, 'valor_new': None, 'valor_old': float(hora_value)}])
         self.df_data_edit=pd.concat([self.df_data_edit,df_add],axis=0, ignore_index=True)

         return change
      except Exception as e:
         raise SystemError('Error al ___add_data_edit: {}. Sentido = {}, hora={}, valor={}'.format(e, sentido_label,hora_int,hora_value))

   def get_QStandardItems(self,value):
      item=QStandardItem(value)
      item.setEditable(False)
      item.setSelectable(True)


      return item

   def Hide_Console(self):
      try:
         import win32console
         import win32gui
         win = win32console.GetConsoleWindow()
         win32gui.ShowWindow(win, 0)

         #win32gui.CloseWindow()
      except:
         pass

   def getQTableWidgetSize(self, tabla):
      w = tabla.verticalHeader().width() + 4  # +4 seems to be needed
      for i in range(tabla.columnCount()):
         w += tabla.columnWidth(i)  # seems to include gridline (on my machine)
      h = tabla.horizontalHeader().height() + 4
      for i in range(tabla.rowCount()):
         h += tabla.rowHeight(i)
      return QSize(w, h)

   def edit_fecha(self):
      self.pushButton_Save_Fecha.setVisible(True)
      self.dateEdit.setEnabled(True)
      self.pushButton_EditFecha.setVisible(False)
      self.fecha = self.dateEdit.date().toPython()

      self.fr_es.periodo= self.fecha
      self.es_fr.periodo = self.fecha
      self.pt_es.periodo = self.fecha
      self.es_pt.periodo = self.fecha

   def save_fecha(self):
      self.pushButton_Save_Fecha.setVisible(False)
      self.dateEdit.setEnabled(False)
      self.pushButton_EditFecha.setVisible(True)

   def cargar_xml_capdoc(self):
      try:
         # self.fecha=self.dateEdit.date().toPython()
         # self.get_path_fichero_xml()
         # if not os.path.exists(self.path_xml_capDoc):
         #    QMessageBox.warning(self, __appname__, 'El archivo no existe : {}'.format(self.path_xml_capDoc))
         # else:
         #    self.pushButton_EditTable.setVisible(True)
         #    self.pushButton_GenTable.setVisible(True)

         try:
            self.edit_informacion_hora(eneble=False)
            self.lectura_fichero_SWE_D2_CapDoc_Prop()

            # for col in self.df_table_ini.columns.values:
            #    hora =self.df_table_ini[col].iloc[0]
            #    if hora ==None:
            #       self.df_table_ini.drop(col, axis=1, inplace=True)

            self.columns_df= list(self.df_table_ini.columns.values)
            self.load_tableWiget(df=self.df_table_ini)
         except Exception as e:
            raise SystemError('{}'.format(e))

         self.pushButton_EditTable.setVisible(True)
         self.pushButton_GenTable.setVisible(True)

      except Exception as e:
         QMessageBox.warning(self, __appname__, 'Error cargar_xml_capdoc : {}'.format(e))

   def generar_xml_salida(self):
      try:
         pass
      except Exception as e :
         raise SystemError('Error al generar_xml_salida : {}'.format(e))

   def edit_table(self,enable):
      self.pushButton_SaveTable.setVisible(enable)
      self.pushButton_EditTable.setVisible(not enable)
      self.pushButton_GenTable.setVisible(not enable)
      self.pushButton_LoadTable.setVisible(not enable)

      if enable:
         self.tableWidget.setEditTriggers(QTableWidget.AllEditTriggers)
      #self.tableWidget.setSelectionMode(QTableWidget.SingleSelection)

   def guardar_table(self):
      try:
         self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)

         ok =self.get_table()
         if ok:

            df_edit = self.df_data_edit.loc[self.df_data_edit['valor_new'] !=None]

            class_element=None
            for index, row in self.df_data_edit.iterrows():
               hora=row['hora']
               if row['sentido']=='ES -> FR':
                  class_element = self.es_fr
               elif row['sentido']=='FR -> ES':
                  class_element = self.fr_es
               elif row['sentido']=='ES -> PT':
                  class_element = self.es_pt
               elif row['sentido'] == 'PT -> ES':
                  class_element = self.pt_es

               list_ele=class_element.get_list_elementos()
               list_class_ele= filter(lambda x: x.hora==hora,list_ele)
               for x in list_class_ele:  # type: Elementos_UI
                  if str(row['valor_new']) !=str(np.nan):
                     x.edit=True
                     x.value_potencia=row['valor_new']
                     x.enable(enable=True)
                     x.load_comboBox_Data()
                  else:
                     x.value_potencia = row['valor_old']

         self.edit_table(enable=False)

      except Exception as e:
         raise SystemError('Error al guardar la tabla: {}'.format(e))

   def edit_informacion_hora(self, eneble):

      for x in self.es_fr.get_list_elementos():
         x.enable(eneble)
         x.clear_element()

      for x in self.fr_es.get_list_elementos():
         x.enable(eneble)
         x.clear_element()

      for x in self.es_pt.get_list_elementos():
         x.enable(eneble)
         x.clear_element()

      for x in self.pt_es.get_list_elementos():
         x.enable(eneble)
         x.clear_element()

   def load_comboBox(self):

      for x in self.es_fr.get_list_elementos():
         x.elementos.load_comboBox_Data()

      for x in self.fr_es.get_list_elementos():
         x.elementos.load_comboBox_Data()

      for x in self.es_pt.get_list_elementos():
         x.elementos.load_comboBox_Data()

      for x in self.pt_es.get_list_elementos():
         x.elementos.load_comboBox_Data()

   def lectura_fichero_SWE_D2_CapDoc_Prop(self):

      try:
         dir = Rutas().ruta_input_xml_coreso
         fileObj = QFileDialog.getOpenFileName(self, " Selecione el xml CapDoc", dir=dir,
                                               filter="Archivo XML (*.xml)")
         path=fileObj[0]

         class_info_xml=lectura_SWE_D2_CapDoc_Prop(path = path)
         self.df_table_ini = InfoXML_to_Dataframe(info_xml=class_info_xml)
      except Exception as e:
         raise SystemError('Error lectura_fichero_SWE_D2_CapDoc_Prop : {}'.format(e))


def main():
   QCoreApplication.setApplicationName("TTC_CNE")
   QCoreApplication.setApplicationVersion(version)

   try:
      form =None
      app = QApplication(sys.argv)
      form = Main()
      form.show()
      sys.exit(app.exec_())
   except Exception as e:
      try:
         print (e)
         if form !=None:
            QMessageBox.critical(app, __appname__, u'Error no controlado: {}'.format(e))
      except Exception as e:
         print (e)

if __name__ == "__main__":
    main()


class ES_FR():

   def __init__(self,ui, periodo=''):
      """

      :param ui:
      :type ui: Ui_MainWindow
      :param periodo:
      """
      self.ui=ui

      self.domain_in = Domain.ES
      self.domain_out = Domain.FR
      self.periodo = periodo

      self.hora_00 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_1,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_1,
                                  reason_code=self.ui.comboBox_RC_ESFR_1, reason_text=self.ui.plainTextEdit_RT_ESFR_1,
                                  expla_code=self.ui.comboBox_EC_ESFR_1, expla_text=self.ui.plainTextEdit_ET_ESFR_1,hora=0)

      self.hora_01 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_2,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_2,
                                  reason_code=self.ui.comboBox_RC_ESFR_2, reason_text=self.ui.plainTextEdit_RT_ESFR_2,
                                  expla_code=self.ui.comboBox_EC_ESFR_2, expla_text=self.ui.plainTextEdit_ET_ESFR_2,hora=1)

      self.hora_02 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_3,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_3,
                                  reason_code=self.ui.comboBox_RC_ESFR_3, reason_text=self.ui.plainTextEdit_RT_ESFR_3,
                                  expla_code=self.ui.comboBox_EC_ESFR_3, expla_text=self.ui.plainTextEdit_ET_ESFR_3,hora=2)

      self.hora_03 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_4,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_4,
                                  reason_code=self.ui.comboBox_RC_ESFR_4, reason_text=self.ui.plainTextEdit_RT_ESFR_4,
                                  expla_code=self.ui.comboBox_EC_ESFR_4, expla_text=self.ui.plainTextEdit_ET_ESFR_4,hora=3)

      self.hora_04 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_5,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_5,
                                  reason_code=self.ui.comboBox_RC_ESFR_5, reason_text=self.ui.plainTextEdit_RT_ESFR_5,
                                  expla_code=self.ui.comboBox_EC_ESFR_5, expla_text=self.ui.plainTextEdit_ET_ESFR_5,hora=4)

      self.hora_05 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_6,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_6,
                                  reason_code=self.ui.comboBox_RC_ESFR_6, reason_text=self.ui.plainTextEdit_RT_ESFR_6,
                                  expla_code=self.ui.comboBox_EC_ESFR_6, expla_text=self.ui.plainTextEdit_ET_ESFR_6,hora=5)

      self.hora_06 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_7,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_7,
                                  reason_code=self.ui.comboBox_RC_ESFR_7, reason_text=self.ui.plainTextEdit_RT_ESFR_7,
                                  expla_code=self.ui.comboBox_EC_ESFR_7, expla_text=self.ui.plainTextEdit_ET_ESFR_7,hora=6)
      self.hora_07 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_8,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_8,
                                  reason_code=self.ui.comboBox_RC_ESFR_8, reason_text=self.ui.plainTextEdit_RT_ESFR_8,
                                  expla_code=self.ui.comboBox_EC_ESFR_8, expla_text=self.ui.plainTextEdit_ET_ESFR_8,hora=7)
      self.hora_08 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_9,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_9,
                                  reason_code=self.ui.comboBox_RC_ESFR_9, reason_text=self.ui.plainTextEdit_RT_ESFR_9,
                                  expla_code=self.ui.comboBox_EC_ESFR_9, expla_text=self.ui.plainTextEdit_ET_ESFR_9,hora=8)

      self.hora_09 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_10,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_10,
                                  reason_code=self.ui.comboBox_RC_ESFR_10, reason_text=self.ui.plainTextEdit_RT_ESFR_10,
                                  expla_code=self.ui.comboBox_EC_ESFR_10, expla_text=self.ui.plainTextEdit_ET_ESFR_10,hora=9)

      self.hora_10 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_11,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_11,
                                  reason_code=self.ui.comboBox_RC_ESFR_11, reason_text=self.ui.plainTextEdit_RT_ESFR_11,
                                  expla_code=self.ui.comboBox_EC_ESFR_11, expla_text=self.ui.plainTextEdit_ET_ESFR_11,hora=10)

      self.hora_11 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_12,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_12,
                                  reason_code=self.ui.comboBox_RC_ESFR_12, reason_text=self.ui.plainTextEdit_RT_ESFR_12,
                                  expla_code=self.ui.comboBox_EC_ESFR_12, expla_text=self.ui.plainTextEdit_ET_ESFR_12,hora=11)

      self.hora_12 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_13,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_13,
                                  reason_code=self.ui.comboBox_RC_ESFR_13, reason_text=self.ui.plainTextEdit_RT_ESFR_13,
                                  expla_code=self.ui.comboBox_EC_ESFR_13, expla_text=self.ui.plainTextEdit_ET_ESFR_13,hora=12)

      self.hora_13 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_14,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_14,
                                  reason_code=self.ui.comboBox_RC_ESFR_14, reason_text=self.ui.plainTextEdit_RT_ESFR_14,
                                  expla_code=self.ui.comboBox_EC_ESFR_14, expla_text=self.ui.plainTextEdit_ET_ESFR_14,hora=13)

      self.hora_14 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_15,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_15,
                                  reason_code=self.ui.comboBox_RC_ESFR_15, reason_text=self.ui.plainTextEdit_RT_ESFR_15,
                                  expla_code=self.ui.comboBox_EC_ESFR_15, expla_text=self.ui.plainTextEdit_ET_ESFR_15,hora=14)

      self.hora_15 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_16,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_16,
                                  reason_code=self.ui.comboBox_RC_ESFR_16, reason_text=self.ui.plainTextEdit_RT_ESFR_16,
                                  expla_code=self.ui.comboBox_EC_ESFR_16, expla_text=self.ui.plainTextEdit_ET_ESFR_16,hora=15)

      self.hora_16 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_17,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_17,
                                  reason_code=self.ui.comboBox_RC_ESFR_17, reason_text=self.ui.plainTextEdit_RT_ESFR_17,
                                  expla_code=self.ui.comboBox_EC_ESFR_17, expla_text=self.ui.plainTextEdit_ET_ESFR_17,hora=16)

      self.hora_17 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_18,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_18,
                                  reason_code=self.ui.comboBox_RC_ESFR_18, reason_text=self.ui.plainTextEdit_RT_ESFR_18,
                                  expla_code=self.ui.comboBox_EC_ESFR_18, expla_text=self.ui.plainTextEdit_ET_ESFR_18,hora=17)

      self.hora_18 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_19,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_19,
                                  reason_code=self.ui.comboBox_RC_ESFR_19, reason_text=self.ui.plainTextEdit_RT_ESFR_19,
                                  expla_code=self.ui.comboBox_EC_ESFR_19, expla_text=self.ui.plainTextEdit_ET_ESFR_19,hora=18)

      self.hora_19 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_20,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_20,
                                  reason_code=self.ui.comboBox_RC_ESFR_20, reason_text=self.ui.plainTextEdit_RT_ESFR_20,
                                  expla_code=self.ui.comboBox_EC_ESFR_20, expla_text=self.ui.plainTextEdit_ET_ESFR_20,hora=19)
      self.hora_20 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_21,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_21,
                                  reason_code=self.ui.comboBox_RC_ESFR_21, reason_text=self.ui.plainTextEdit_RT_ESFR_21,
                                  expla_code=self.ui.comboBox_EC_ESFR_21, expla_text=self.ui.plainTextEdit_ET_ESFR_21,hora=20)

      self.hora_21 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_22,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_22,
                                  reason_code=self.ui.comboBox_RC_ESFR_22, reason_text=self.ui.plainTextEdit_RT_ESFR_22,
                                  expla_code=self.ui.comboBox_EC_ESFR_22, expla_text=self.ui.plainTextEdit_ET_ESFR_22,hora=21)

      self.hora_22 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_23,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_23,
                                  reason_code=self.ui.comboBox_RC_ESFR_23, reason_text=self.ui.plainTextEdit_RT_ESFR_23,
                                  expla_code=self.ui.comboBox_EC_ESFR_23, expla_text=self.ui.plainTextEdit_ET_ESFR_23,hora=22)

      self.hora_23 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_24,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_24,
                                  reason_code=self.ui.comboBox_RC_ESFR_24, reason_text=self.ui.plainTextEdit_RT_ESFR_24,
                                  expla_code=self.ui.comboBox_EC_ESFR_24, expla_text=self.ui.plainTextEdit_ET_ESFR_24,hora=23)

      self.hora_24 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESFR_25,
                                  combox_con_limitante=self.ui.comboBox_CL_ESFR_25,
                                  reason_code=self.ui.comboBox_RC_ESFR_25, reason_text=self.ui.plainTextEdit_RT_ESFR_25,
                                  expla_code=self.ui.comboBox_EC_ESFR_25, expla_text=self.ui.plainTextEdit_ET_ESFR_25, hora=24)


   def get_list_elementos(self):
         reul=[]
         reul.append(self.hora_00)
         reul.append(self.hora_01)
         reul.append(self.hora_02)
         reul.append(self.hora_03)
         reul.append(self.hora_04)
         reul.append(self.hora_05)
         reul.append(self.hora_06)
         reul.append(self.hora_07)
         reul.append(self.hora_08)
         reul.append(self.hora_09)
         reul.append(self.hora_10)
         reul.append(self.hora_11)
         reul.append(self.hora_12)
         reul.append(self.hora_13)
         reul.append(self.hora_14)
         reul.append(self.hora_15)
         reul.append(self.hora_16)
         reul.append(self.hora_17)
         reul.append(self.hora_18)
         reul.append(self.hora_19)
         reul.append(self.hora_20)
         reul.append(self.hora_21)
         reul.append(self.hora_22)
         reul.append(self.hora_23)
         reul.append(self.hora_24)


         return reul

class FR_ES():
   def __init__(self,ui, periodo=''):
      """

      :param ui:
      :type ui: Ui_MainWindow
      :param periodo:
      """
      self.ui=ui

      self.domain_in = Domain.FR
      self.domain_out = Domain.ES
      self.periodo = periodo

      self.hora_00 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_1,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_1,
                                  reason_code=self.ui.comboBox_RC_FRES_1, reason_text=self.ui.plainTextEdit_RT_FRES_1,
                                  expla_code=self.ui.comboBox_EC_FRES_1, expla_text=self.ui.plainTextEdit_ET_FRES_1, hora=0)
      self.hora_01 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_2,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_2,
                                  reason_code=self.ui.comboBox_RC_FRES_2, reason_text=self.ui.plainTextEdit_RT_FRES_2,
                                  expla_code=self.ui.comboBox_EC_FRES_2, expla_text=self.ui.plainTextEdit_ET_FRES_2, hora=1)
      self.hora_02 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_3,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_3,
                                  reason_code=self.ui.comboBox_RC_FRES_3, reason_text=self.ui.plainTextEdit_RT_FRES_3,
                                  expla_code=self.ui.comboBox_EC_FRES_3, expla_text=self.ui.plainTextEdit_ET_FRES_3, hora=2)
      self.hora_03 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_4,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_4,
                                  reason_code=self.ui.comboBox_RC_FRES_4, reason_text=self.ui.plainTextEdit_RT_FRES_4,
                                  expla_code=self.ui.comboBox_EC_FRES_4, expla_text=self.ui.plainTextEdit_ET_FRES_4, hora=3)
      self.hora_04 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_5,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_5,
                                  reason_code=self.ui.comboBox_RC_FRES_5, reason_text=self.ui.plainTextEdit_RT_FRES_5,
                                  expla_code=self.ui.comboBox_EC_FRES_5, expla_text=self.ui.plainTextEdit_ET_FRES_5, hora=4)
      self.hora_05 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_6,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_6,
                                  reason_code=self.ui.comboBox_RC_FRES_6, reason_text=self.ui.plainTextEdit_RT_FRES_6,
                                  expla_code=self.ui.comboBox_EC_FRES_6, expla_text=self.ui.plainTextEdit_ET_FRES_6, hora=5)
      self.hora_06 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_7,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_7,
                                  reason_code=self.ui.comboBox_RC_FRES_7, reason_text=self.ui.plainTextEdit_RT_FRES_7,
                                  expla_code=self.ui.comboBox_EC_FRES_7, expla_text=self.ui.plainTextEdit_ET_FRES_7, hora=6)
      self.hora_07 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_8,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_8,
                                  reason_code=self.ui.comboBox_RC_FRES_8, reason_text=self.ui.plainTextEdit_RT_FRES_8,
                                  expla_code=self.ui.comboBox_EC_FRES_8, expla_text=self.ui.plainTextEdit_ET_FRES_8, hora=7)
      self.hora_08 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_9,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_9,
                                  reason_code=self.ui.comboBox_RC_FRES_9, reason_text=self.ui.plainTextEdit_RT_FRES_9,
                                  expla_code=self.ui.comboBox_EC_FRES_9, expla_text=self.ui.plainTextEdit_ET_FRES_9, hora=8)
      self.hora_09 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_10,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_10,
                                  reason_code=self.ui.comboBox_RC_FRES_10, reason_text=self.ui.plainTextEdit_RT_FRES_10,
                                  expla_code=self.ui.comboBox_EC_FRES_10, expla_text=self.ui.plainTextEdit_ET_FRES_10, hora=9)
      self.hora_10 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_11,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_11,
                                  reason_code=self.ui.comboBox_RC_FRES_11, reason_text=self.ui.plainTextEdit_RT_FRES_11,
                                  expla_code=self.ui.comboBox_EC_FRES_11, expla_text=self.ui.plainTextEdit_ET_FRES_11, hora=10)
      self.hora_11 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_12,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_12,
                                  reason_code=self.ui.comboBox_RC_FRES_12, reason_text=self.ui.plainTextEdit_RT_FRES_12,
                                  expla_code=self.ui.comboBox_EC_FRES_12, expla_text=self.ui.plainTextEdit_ET_FRES_12, hora=11)
      self.hora_12 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_13,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_13,
                                  reason_code=self.ui.comboBox_RC_FRES_13, reason_text=self.ui.plainTextEdit_RT_FRES_13,
                                  expla_code=self.ui.comboBox_EC_FRES_13, expla_text=self.ui.plainTextEdit_ET_FRES_13, hora=12)
      self.hora_13 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_14,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_14,
                                  reason_code=self.ui.comboBox_RC_FRES_14, reason_text=self.ui.plainTextEdit_RT_FRES_14,
                                  expla_code=self.ui.comboBox_EC_FRES_14, expla_text=self.ui.plainTextEdit_ET_FRES_14, hora=13)
      self.hora_14 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_15,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_15,
                                  reason_code=self.ui.comboBox_RC_FRES_15, reason_text=self.ui.plainTextEdit_RT_FRES_15,
                                  expla_code=self.ui.comboBox_EC_FRES_15, expla_text=self.ui.plainTextEdit_ET_FRES_15, hora=14)
      self.hora_15 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_16,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_16,
                                  reason_code=self.ui.comboBox_RC_FRES_16, reason_text=self.ui.plainTextEdit_RT_FRES_16,
                                  expla_code=self.ui.comboBox_EC_FRES_16, expla_text=self.ui.plainTextEdit_ET_FRES_16, hora=15)
      self.hora_16 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_17,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_17,
                                  reason_code=self.ui.comboBox_RC_FRES_17, reason_text=self.ui.plainTextEdit_RT_FRES_17,
                                  expla_code=self.ui.comboBox_EC_FRES_17, expla_text=self.ui.plainTextEdit_ET_FRES_17, hora=16)
      self.hora_17 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_18,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_18,
                                  reason_code=self.ui.comboBox_RC_FRES_18, reason_text=self.ui.plainTextEdit_RT_FRES_18,
                                  expla_code=self.ui.comboBox_EC_FRES_18, expla_text=self.ui.plainTextEdit_ET_FRES_18, hora=17)
      self.hora_18 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_19,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_19,
                                  reason_code=self.ui.comboBox_RC_FRES_19, reason_text=self.ui.plainTextEdit_RT_FRES_19,
                                  expla_code=self.ui.comboBox_EC_FRES_19, expla_text=self.ui.plainTextEdit_ET_FRES_19, hora=18)
      self.hora_19 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_20,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_20,
                                  reason_code=self.ui.comboBox_RC_FRES_20, reason_text=self.ui.plainTextEdit_RT_FRES_20,
                                  expla_code=self.ui.comboBox_EC_FRES_20, expla_text=self.ui.plainTextEdit_ET_FRES_20, hora=19)
      self.hora_20 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_21,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_21,
                                  reason_code=self.ui.comboBox_RC_FRES_21, reason_text=self.ui.plainTextEdit_RT_FRES_21,
                                  expla_code=self.ui.comboBox_EC_FRES_21, expla_text=self.ui.plainTextEdit_ET_FRES_21, hora=20)
      self.hora_21 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_22,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_22,
                                  reason_code=self.ui.comboBox_RC_FRES_22, reason_text=self.ui.plainTextEdit_RT_FRES_22,
                                  expla_code=self.ui.comboBox_EC_FRES_22, expla_text=self.ui.plainTextEdit_ET_FRES_22, hora=21)
      self.hora_22 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_23,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_23,
                                  reason_code=self.ui.comboBox_RC_FRES_23, reason_text=self.ui.plainTextEdit_RT_FRES_23,
                                  expla_code=self.ui.comboBox_EC_FRES_23, expla_text=self.ui.plainTextEdit_ET_FRES_23, hora=22)
      self.hora_23 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_24,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_24,
                                  reason_code=self.ui.comboBox_RC_FRES_24, reason_text=self.ui.plainTextEdit_RT_FRES_24,
                                  expla_code=self.ui.comboBox_EC_FRES_24, expla_text=self.ui.plainTextEdit_ET_FRES_24, hora=23)
      self.hora_24 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_FRES_25,
                                  combox_con_limitante=self.ui.comboBox_CL_FRES_25,
                                  reason_code=self.ui.comboBox_RC_FRES_25, reason_text=self.ui.plainTextEdit_RT_FRES_25,
                                  expla_code=self.ui.comboBox_EC_FRES_25, expla_text=self.ui.plainTextEdit_ET_FRES_25, hora=24)

   def get_list_elementos(self):
      reul = []
      reul.append(self.hora_00)
      reul.append(self.hora_01)
      reul.append(self.hora_02)
      reul.append(self.hora_03)
      reul.append(self.hora_04)
      reul.append(self.hora_05)
      reul.append(self.hora_06)
      reul.append(self.hora_07)
      reul.append(self.hora_08)
      reul.append(self.hora_09)
      reul.append(self.hora_10)
      reul.append(self.hora_11)
      reul.append(self.hora_12)
      reul.append(self.hora_13)
      reul.append(self.hora_14)
      reul.append(self.hora_15)
      reul.append(self.hora_16)
      reul.append(self.hora_17)
      reul.append(self.hora_18)
      reul.append(self.hora_19)
      reul.append(self.hora_20)
      reul.append(self.hora_21)
      reul.append(self.hora_22)
      reul.append(self.hora_23)
      reul.append(self.hora_24)

      return reul

class ES_PT():
   def __init__(self,ui, periodo=''):
      """

      :param ui:
      :type ui: Ui_MainWindow
      :param periodo:
      """
      self.ui=ui

      self.domain_in = Domain.ES
      self.domain_out = Domain.PT
      self.periodo = periodo

      self.hora_00 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_1,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_1,
                                  reason_code=self.ui.comboBox_RC_ESPT_1, reason_text=self.ui.plainTextEdit_RT_ESPT_1,
                                  expla_code=self.ui.comboBox_EC_ESPT_1, expla_text=self.ui.plainTextEdit_ET_ESPT_1,hora=0)
      self.hora_01 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_2,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_2,
                                  reason_code=self.ui.comboBox_RC_ESPT_2, reason_text=self.ui.plainTextEdit_RT_ESPT_2,
                                  expla_code=self.ui.comboBox_EC_ESPT_2, expla_text=self.ui.plainTextEdit_ET_ESPT_2,hora=1)
      self.hora_02 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_3,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_3,
                                  reason_code=self.ui.comboBox_RC_ESPT_3, reason_text=self.ui.plainTextEdit_RT_ESPT_3,
                                  expla_code=self.ui.comboBox_EC_ESPT_3, expla_text=self.ui.plainTextEdit_ET_ESPT_3,hora=2)
      self.hora_03 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_4,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_4,
                                  reason_code=self.ui.comboBox_RC_ESPT_4, reason_text=self.ui.plainTextEdit_RT_ESPT_4,
                                  expla_code=self.ui.comboBox_EC_ESPT_4, expla_text=self.ui.plainTextEdit_ET_ESPT_4,hora=3)
      self.hora_04 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_5,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_5,
                                  reason_code=self.ui.comboBox_RC_ESPT_5, reason_text=self.ui.plainTextEdit_RT_ESPT_5,
                                  expla_code=self.ui.comboBox_EC_ESPT_5, expla_text=self.ui.plainTextEdit_ET_ESPT_5,hora=4)
      self.hora_05 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_6,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_6,
                                  reason_code=self.ui.comboBox_RC_ESPT_6, reason_text=self.ui.plainTextEdit_RT_ESPT_6,
                                  expla_code=self.ui.comboBox_EC_ESPT_6, expla_text=self.ui.plainTextEdit_ET_ESPT_6,hora=5)
      self.hora_06 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_7,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_7,
                                  reason_code=self.ui.comboBox_RC_ESPT_7, reason_text=self.ui.plainTextEdit_RT_ESPT_7,
                                  expla_code=self.ui.comboBox_EC_ESPT_7, expla_text=self.ui.plainTextEdit_ET_ESPT_7,hora=6)
      self.hora_07 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_8,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_8,
                                  reason_code=self.ui.comboBox_RC_ESPT_8, reason_text=self.ui.plainTextEdit_RT_ESPT_8,
                                  expla_code=self.ui.comboBox_EC_ESPT_8, expla_text=self.ui.plainTextEdit_ET_ESPT_8,hora=7)
      self.hora_08 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_9,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_9,
                                  reason_code=self.ui.comboBox_RC_ESPT_9, reason_text=self.ui.plainTextEdit_RT_ESPT_9,
                                  expla_code=self.ui.comboBox_EC_ESPT_9, expla_text=self.ui.plainTextEdit_ET_ESPT_9,hora=8)
      self.hora_09 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_10,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_10,
                                  reason_code=self.ui.comboBox_RC_ESPT_10, reason_text=self.ui.plainTextEdit_RT_ESPT_10,
                                  expla_code=self.ui.comboBox_EC_ESPT_10, expla_text=self.ui.plainTextEdit_ET_ESPT_10,hora=9)
      self.hora_10 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_11,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_11,
                                  reason_code=self.ui.comboBox_RC_ESPT_11, reason_text=self.ui.plainTextEdit_RT_ESPT_11,
                                  expla_code=self.ui.comboBox_EC_ESPT_11, expla_text=self.ui.plainTextEdit_ET_ESPT_11,hora=10)
      self.hora_11 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_12,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_12,
                                  reason_code=self.ui.comboBox_RC_ESPT_12, reason_text=self.ui.plainTextEdit_RT_ESPT_12,
                                  expla_code=self.ui.comboBox_EC_ESPT_12, expla_text=self.ui.plainTextEdit_ET_ESPT_12,hora=11)
      self.hora_12 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_13,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_13,
                                  reason_code=self.ui.comboBox_RC_ESPT_13, reason_text=self.ui.plainTextEdit_RT_ESPT_13,
                                  expla_code=self.ui.comboBox_EC_ESPT_13, expla_text=self.ui.plainTextEdit_ET_ESPT_13,hora=12)
      self.hora_13 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_14,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_14,
                                  reason_code=self.ui.comboBox_RC_ESPT_14, reason_text=self.ui.plainTextEdit_RT_ESPT_14,
                                  expla_code=self.ui.comboBox_EC_ESPT_14, expla_text=self.ui.plainTextEdit_ET_ESPT_14,hora=13)
      self.hora_14 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_15,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_15,
                                  reason_code=self.ui.comboBox_RC_ESPT_15, reason_text=self.ui.plainTextEdit_RT_ESPT_15,
                                  expla_code=self.ui.comboBox_EC_ESPT_15, expla_text=self.ui.plainTextEdit_ET_ESPT_15,hora=14)
      self.hora_15 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_16,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_16,
                                  reason_code=self.ui.comboBox_RC_ESPT_16, reason_text=self.ui.plainTextEdit_RT_ESPT_16,
                                  expla_code=self.ui.comboBox_EC_ESPT_16, expla_text=self.ui.plainTextEdit_ET_ESPT_16,hora=15)
      self.hora_16 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_17,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_17,
                                  reason_code=self.ui.comboBox_RC_ESPT_17, reason_text=self.ui.plainTextEdit_RT_ESPT_17,
                                  expla_code=self.ui.comboBox_EC_ESPT_17, expla_text=self.ui.plainTextEdit_ET_ESPT_17,hora=16)
      self.hora_17 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_18,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_18,
                                  reason_code=self.ui.comboBox_RC_ESPT_18, reason_text=self.ui.plainTextEdit_RT_ESPT_18,
                                  expla_code=self.ui.comboBox_EC_ESPT_18, expla_text=self.ui.plainTextEdit_ET_ESPT_18,hora=17)
      self.hora_18 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_19,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_19,
                                  reason_code=self.ui.comboBox_RC_ESPT_19, reason_text=self.ui.plainTextEdit_RT_ESPT_19,
                                  expla_code=self.ui.comboBox_EC_ESPT_19, expla_text=self.ui.plainTextEdit_ET_ESPT_19,hora=18)
      self.hora_19 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_20,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_20,
                                  reason_code=self.ui.comboBox_RC_ESPT_20, reason_text=self.ui.plainTextEdit_RT_ESPT_20,
                                  expla_code=self.ui.comboBox_EC_ESPT_20, expla_text=self.ui.plainTextEdit_ET_ESPT_20,hora=19)
      self.hora_20 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_21,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_21,
                                  reason_code=self.ui.comboBox_RC_ESPT_21, reason_text=self.ui.plainTextEdit_RT_ESPT_21,
                                  expla_code=self.ui.comboBox_EC_ESPT_21, expla_text=self.ui.plainTextEdit_ET_ESPT_21,hora=20)
      self.hora_21 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_22,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_22,
                                  reason_code=self.ui.comboBox_RC_ESPT_22, reason_text=self.ui.plainTextEdit_RT_ESPT_22,
                                  expla_code=self.ui.comboBox_EC_ESPT_22, expla_text=self.ui.plainTextEdit_ET_ESPT_22,hora=21)
      self.hora_22 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_23,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_23,
                                  reason_code=self.ui.comboBox_RC_ESPT_23, reason_text=self.ui.plainTextEdit_RT_ESPT_23,
                                  expla_code=self.ui.comboBox_EC_ESPT_23, expla_text=self.ui.plainTextEdit_ET_ESPT_23,hora=22)
      self.hora_23 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_24,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_24,
                                  reason_code=self.ui.comboBox_RC_ESPT_24, reason_text=self.ui.plainTextEdit_RT_ESPT_24,
                                  expla_code=self.ui.comboBox_EC_ESPT_24, expla_text=self.ui.plainTextEdit_ET_ESPT_24,hora=23)
      self.hora_24 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_ESPT_25,
                                  combox_con_limitante=self.ui.comboBox_CL_ESPT_25,
                                  reason_code=self.ui.comboBox_RC_ESPT_25, reason_text=self.ui.plainTextEdit_RT_ESPT_25,
                                  expla_code=self.ui.comboBox_EC_ESPT_25, expla_text=self.ui.plainTextEdit_ET_ESPT_25,hora=24)

   def get_list_elementos(self):
      reul = []
      reul.append(self.hora_00)
      reul.append(self.hora_01)
      reul.append(self.hora_02)
      reul.append(self.hora_03)
      reul.append(self.hora_04)
      reul.append(self.hora_05)
      reul.append(self.hora_06)
      reul.append(self.hora_07)
      reul.append(self.hora_08)
      reul.append(self.hora_09)
      reul.append(self.hora_10)
      reul.append(self.hora_11)
      reul.append(self.hora_12)
      reul.append(self.hora_13)
      reul.append(self.hora_14)
      reul.append(self.hora_15)
      reul.append(self.hora_16)
      reul.append(self.hora_17)
      reul.append(self.hora_18)
      reul.append(self.hora_19)
      reul.append(self.hora_20)
      reul.append(self.hora_21)
      reul.append(self.hora_22)
      reul.append(self.hora_23)
      reul.append(self.hora_24)

      return reul

class PT_ES():
   def __init__(self,ui, periodo=''):
      """

      :param ui:
      :type ui: Ui_MainWindow
      :param periodo:
      """
      self.ui=ui

      self.domain_in = Domain.PT
      self.domain_out = Domain.ES
      self.periodo = periodo

      self.hora_00 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_1,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_1,
                                  reason_code=self.ui.comboBox_RC_PTES_1, reason_text=self.ui.plainTextEdit_RT_PTES_1,
                                  expla_code=self.ui.comboBox_EC_PTES_1, expla_text=self.ui.plainTextEdit_ET_PTES_1, hora=0)
      self.hora_01 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_2,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_2,
                                  reason_code=self.ui.comboBox_RC_PTES_2, reason_text=self.ui.plainTextEdit_RT_PTES_2,
                                  expla_code=self.ui.comboBox_EC_PTES_2, expla_text=self.ui.plainTextEdit_ET_PTES_2, hora=1)
      self.hora_02 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_3,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_3,
                                  reason_code=self.ui.comboBox_RC_PTES_3, reason_text=self.ui.plainTextEdit_RT_PTES_3,
                                  expla_code=self.ui.comboBox_EC_PTES_3, expla_text=self.ui.plainTextEdit_ET_PTES_3, hora=2)
      self.hora_03 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_4,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_4,
                                  reason_code=self.ui.comboBox_RC_PTES_4, reason_text=self.ui.plainTextEdit_RT_PTES_4,
                                  expla_code=self.ui.comboBox_EC_PTES_4, expla_text=self.ui.plainTextEdit_ET_PTES_4, hora=3)
      self.hora_04 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_5,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_5,
                                  reason_code=self.ui.comboBox_RC_PTES_5, reason_text=self.ui.plainTextEdit_RT_PTES_5,
                                  expla_code=self.ui.comboBox_EC_PTES_5, expla_text=self.ui.plainTextEdit_ET_PTES_5, hora=4)
      self.hora_05 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_6,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_6,
                                  reason_code=self.ui.comboBox_RC_PTES_6, reason_text=self.ui.plainTextEdit_RT_PTES_6,
                                  expla_code=self.ui.comboBox_EC_PTES_6, expla_text=self.ui.plainTextEdit_ET_PTES_6, hora=5)
      self.hora_06 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_7,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_7,
                                  reason_code=self.ui.comboBox_RC_PTES_7, reason_text=self.ui.plainTextEdit_RT_PTES_7,
                                  expla_code=self.ui.comboBox_EC_PTES_7, expla_text=self.ui.plainTextEdit_ET_PTES_7, hora=6)
      self.hora_07 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_8,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_8,
                                  reason_code=self.ui.comboBox_RC_PTES_8, reason_text=self.ui.plainTextEdit_RT_PTES_8,
                                  expla_code=self.ui.comboBox_EC_PTES_8, expla_text=self.ui.plainTextEdit_ET_PTES_8, hora=7)
      self.hora_08 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_9,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_9,
                                  reason_code=self.ui.comboBox_RC_PTES_9, reason_text=self.ui.plainTextEdit_RT_PTES_9,
                                  expla_code=self.ui.comboBox_EC_PTES_9, expla_text=self.ui.plainTextEdit_ET_PTES_9, hora=8)
      self.hora_09 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_10,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_10,
                                  reason_code=self.ui.comboBox_RC_PTES_10, reason_text=self.ui.plainTextEdit_RT_PTES_10,
                                  expla_code=self.ui.comboBox_EC_PTES_10, expla_text=self.ui.plainTextEdit_ET_PTES_10, hora=9)
      self.hora_10 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_11,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_11,
                                  reason_code=self.ui.comboBox_RC_PTES_11, reason_text=self.ui.plainTextEdit_RT_PTES_11,
                                  expla_code=self.ui.comboBox_EC_PTES_11, expla_text=self.ui.plainTextEdit_ET_PTES_11, hora=10)
      self.hora_11 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_12,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_12,
                                  reason_code=self.ui.comboBox_RC_PTES_12, reason_text=self.ui.plainTextEdit_RT_PTES_12,
                                  expla_code=self.ui.comboBox_EC_PTES_12, expla_text=self.ui.plainTextEdit_ET_PTES_12, hora=11)
      self.hora_12 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_13,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_13,
                                  reason_code=self.ui.comboBox_RC_PTES_13, reason_text=self.ui.plainTextEdit_RT_PTES_13,
                                  expla_code=self.ui.comboBox_EC_PTES_13, expla_text=self.ui.plainTextEdit_ET_PTES_13, hora=12)
      self.hora_13 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_14,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_14,
                                  reason_code=self.ui.comboBox_RC_PTES_14, reason_text=self.ui.plainTextEdit_RT_PTES_14,
                                  expla_code=self.ui.comboBox_EC_PTES_14, expla_text=self.ui.plainTextEdit_ET_PTES_14, hora=13)
      self.hora_14 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_15,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_15,
                                  reason_code=self.ui.comboBox_RC_PTES_15, reason_text=self.ui.plainTextEdit_RT_PTES_15,
                                  expla_code=self.ui.comboBox_EC_PTES_15, expla_text=self.ui.plainTextEdit_ET_PTES_15, hora=14)
      self.hora_15 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_16,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_16,
                                  reason_code=self.ui.comboBox_RC_PTES_16, reason_text=self.ui.plainTextEdit_RT_PTES_16,
                                  expla_code=self.ui.comboBox_EC_PTES_16, expla_text=self.ui.plainTextEdit_ET_PTES_16, hora=15)
      self.hora_16 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_17,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_17,
                                  reason_code=self.ui.comboBox_RC_PTES_17, reason_text=self.ui.plainTextEdit_RT_PTES_17,
                                  expla_code=self.ui.comboBox_EC_PTES_17, expla_text=self.ui.plainTextEdit_ET_PTES_17, hora=16)
      self.hora_17 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_18,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_18,
                                  reason_code=self.ui.comboBox_RC_PTES_18, reason_text=self.ui.plainTextEdit_RT_PTES_18,
                                  expla_code=self.ui.comboBox_EC_PTES_18, expla_text=self.ui.plainTextEdit_ET_PTES_18, hora=17)
      self.hora_18 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_19,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_19,
                                  reason_code=self.ui.comboBox_RC_PTES_19, reason_text=self.ui.plainTextEdit_RT_PTES_19,
                                  expla_code=self.ui.comboBox_EC_PTES_19, expla_text=self.ui.plainTextEdit_ET_PTES_19, hora=18)
      self.hora_19 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_20,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_20,
                                  reason_code=self.ui.comboBox_RC_PTES_20, reason_text=self.ui.plainTextEdit_RT_PTES_20,
                                  expla_code=self.ui.comboBox_EC_PTES_20, expla_text=self.ui.plainTextEdit_ET_PTES_20, hora=19)
      self.hora_20 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_21,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_21,
                                  reason_code=self.ui.comboBox_RC_PTES_21, reason_text=self.ui.plainTextEdit_RT_PTES_21,
                                  expla_code=self.ui.comboBox_EC_PTES_21, expla_text=self.ui.plainTextEdit_ET_PTES_21, hora=20)
      self.hora_21 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_22,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_22,
                                  reason_code=self.ui.comboBox_RC_PTES_22, reason_text=self.ui.plainTextEdit_RT_PTES_22,
                                  expla_code=self.ui.comboBox_EC_PTES_22, expla_text=self.ui.plainTextEdit_ET_PTES_22, hora=21)
      self.hora_22 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_23,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_23,
                                  reason_code=self.ui.comboBox_RC_PTES_23, reason_text=self.ui.plainTextEdit_RT_PTES_23,
                                  expla_code=self.ui.comboBox_EC_PTES_23, expla_text=self.ui.plainTextEdit_ET_PTES_23, hora=22)
      self.hora_23 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_24,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_24,
                                  reason_code=self.ui.comboBox_RC_PTES_24, reason_text=self.ui.plainTextEdit_RT_PTES_24,
                                  expla_code=self.ui.comboBox_EC_PTES_24, expla_text=self.ui.plainTextEdit_ET_PTES_24, hora=23)
      self.hora_24 = Elementos_UI(combox_ele_limitante=self.ui.comboBox_EL_PTES_25,
                                  combox_con_limitante=self.ui.comboBox_CL_PTES_25,
                                  reason_code=self.ui.comboBox_RC_PTES_25, reason_text=self.ui.plainTextEdit_RT_PTES_25,
                                  expla_code=self.ui.comboBox_EC_PTES_25, expla_text=self.ui.plainTextEdit_ET_PTES_25, hora=24)

   def get_list_elementos(self):
      reul = []
      reul.append(self.hora_00)
      reul.append(self.hora_01)
      reul.append(self.hora_02)
      reul.append(self.hora_03)
      reul.append(self.hora_04)
      reul.append(self.hora_05)
      reul.append(self.hora_06)
      reul.append(self.hora_07)
      reul.append(self.hora_08)
      reul.append(self.hora_09)
      reul.append(self.hora_10)
      reul.append(self.hora_11)
      reul.append(self.hora_12)
      reul.append(self.hora_13)
      reul.append(self.hora_14)
      reul.append(self.hora_15)
      reul.append(self.hora_16)
      reul.append(self.hora_17)
      reul.append(self.hora_18)
      reul.append(self.hora_19)
      reul.append(self.hora_20)
      reul.append(self.hora_21)
      reul.append(self.hora_22)
      reul.append(self.hora_23)
      reul.append(self.hora_24)

      return reul



class Elementos_UI():
   def __init__(self,combox_ele_limitante,combox_con_limitante,reason_code,reason_text,expla_code,expla_text,hora, edit=False,value_potencia=None, ):
      """

      :param combox_ele_limitante: QComboBox
      :type combox_ele_limitante: QComboBox
      :param combox_con_limitante: QComboBox
      :type combox_con_limitante: QComboBox
      :param reason_code: QLineEdit
      :type reason_code: QComboBox
      :param reason_text: QPlainTextEdit
      :type reason_text: QPlainTextEdit
      :param expla_code:QPlainTextEdit
      :type expla_code: QComboBox
      :param expla_text:QPlainTextEdit
      :type expla_text: QPlainTextEdit
      """
      self.combox_ele_limitante = combox_ele_limitante
      self.combox_con_limitante = combox_con_limitante
      self.line_reason_code = reason_code
      self.line_reason_text = reason_text
      self.line_expla_code = expla_code
      self.line_expla_text = expla_text
      self.value_potencia=value_potencia
      self.hora=hora
      self.edit=edit


      self.__element_limi=None
      self.__con_limi=None
      self.__reason_code=None
      self.__reason_text=None
      self.__expla_code=None
      self.__expla_text=None

      self.list_mon = df_mon.to_dict('records')
      self.list_co_dict =df_co_dict.to_dict('records')
      self.list_reason_code=list_reason_codes
      self.list_explat_codes =list_explat_codes

   @property
   def element_limi(self):
      return self.__element_limi
   @element_limi.getter
   def element_limi(self):
      self.__element_limi

   @property
   def con_limi(self):
      return self.__con_limi
   @con_limi.getter
   def con_limi(self, value):
      self.__con_limi = value

   @property
   def reason_code(self):
      return self.__reason_code
   @reason_code.getter
   def reason_code(self):
      self.__reason_code

   @property
   def reason_text(self):
      return self.__reason_text
   @reason_text.getter
   def reason_text(self):
      self.__reason_text

   @property
   def expla_cod(self):
      return self.__expla_cod
   @expla_cod.getter
   def expla_cod(self):
      self.__expla_cod

   @property
   def expla_text(self):
      return self.__expla_text

   @expla_cod.getter
   def expla_text(self):
      self.__expla_text

   def enable(self, enable):
      self.combox_ele_limitante.setEnabled(enable)
      self.combox_con_limitante.setEnabled(enable)
      self.line_reason_code.setEnabled(enable)
      self.line_reason_text.setEnabled(enable)
      self.line_expla_code.setEnabled(enable)
      self.line_expla_text.setEnabled(enable)

   def load_comboBox_Ele_Limitante(self):
      self.combox_ele_limitante.setEditable(True)
      self.combox_ele_limitante.setInsertPolicy(QComboBox.NoInsert)
      completer = CustomQCompleter(self.combox_ele_limitante)
      completer.setCompletionMode(QCompleter.PopupCompletion)
      completer.setModel(self.combox_ele_limitante.model())
      self.combox_ele_limitante.setCompleter(completer)

   def load_comboBox_Ele_Con(self):
      self.combox_con_limitante.setEditable(True)
      self.combox_con_limitante.setInsertPolicy(QComboBox.NoInsert)
      completer2 = CustomQCompleter(self.combox_con_limitante)
      completer2.setCompletionMode(QCompleter.PopupCompletion)
      completer2.setModel(self.combox_con_limitante.model())
      self.combox_con_limitante.setCompleter(completer2)

   def load_comboBox_Data(self):

      self.load_comboBox_Ele_Limitante()
      self.combox_ele_limitante.clear()
      self.combox_ele_limitante.addItem('', None)
      for x in self.list_mon:
         DATA = str(x['DESCRIPTION']).replace('[', ' ').replace(']', ' ')
         self.combox_ele_limitante.addItem(DATA, x)

      self.load_comboBox_Ele_Con()
      self.combox_con_limitante.clear()
      self.combox_con_limitante.addItem('', None)
      for x in self.list_co_dict:
         DATA = str(x['name CO Dict'])
         self.combox_con_limitante.addItem(DATA, x)

      self.load_comboBox_ReasonCode()
      self.line_reason_code.clear()
      self.line_reason_code.addItem('', None)
      for x in self.list_reason_code:
         DATA = str('{} - {} '.format(x.code, x.descrip))
         self.line_reason_code.addItem(DATA, x)

      self.load_comboBox_ExplanatCode()
      self.line_expla_code.clear()
      self.line_expla_code.addItem('', None)
      for x in self.list_explat_codes:
         DATA = str('{} - {} '.format(x.code, x.descrip))
         self.line_expla_code.addItem(DATA, x)

   def load_comboBox_ReasonCode(self):
      self.line_reason_code.setEditable(True)
      self.line_reason_code.setInsertPolicy(QComboBox.NoInsert)
      completer = CustomQCompleter(self.line_reason_code)
      completer.setCompletionMode(QCompleter.PopupCompletion)
      completer.setModel(self.line_reason_code.model())
      self.line_reason_code.setCompleter(completer)

   def load_comboBox_ExplanatCode(self):
      self.line_expla_code.setEditable(True)
      self.line_expla_code.setInsertPolicy(QComboBox.NoInsert)
      completer = CustomQCompleter(self.line_expla_code)
      completer.setCompletionMode(QCompleter.PopupCompletion)
      completer.setModel(self.line_expla_code.model())
      self.line_expla_code.setCompleter(completer)

   def clear_element(self):
      self.combox_ele_limitante.clear()
      self.combox_con_limitante.clear()
      self.line_reason_code.clear()
      self.line_reason_text.clear()
      self.line_expla_code.clear()
      self.line_expla_text.clear()


