import unittest
from Software.Entidades.lectura_ficheros import lectura_excel_crack,read_idReport,read_nudosX
from Software.Core.lectura_xml import lectura_SWE_D2_CapDoc_Prop,InfoXML_to_Dataframe, create_XML_CapDoc_by_Plantilla,lectura_SWE_D2_CapDoc_Prop_tree,create_XML_CapDoc

class MyTestCase(unittest.TestCase):
   def test_lectura_xml_inputcoreso(self):

      strff=r"D:\TTC_CNE\Fich_Entrada\20190202_SWE_D2_CapDoc_Prop_REE.xml"

      pruebas = r"D:\TTC_CNE\Fich_Entrada\PRueba_REE.xml"

      info_xml, guid=lectura_SWE_D2_CapDoc_Prop(path=strff)
      info_xml=lectura_SWE_D2_CapDoc_Prop_tree(path=strff)
      df_infoXML=InfoXML_to_Dataframe(info_xml=info_xml)

      create_XML_CapDoc_by_Plantilla(path_input=strff, path_output=pruebas, info_xml=info_xml, acept=True)
      pass

   def test_WRITE_xml_inputcoreso(self):
      strff=r"D:\TTC_CNE\Fich_Entrada\20190202_SWE_D2_CapDoc_Prop_REE.xml"

      pruebas = r"D:\TTC_CNE\Fich_Entrada\PRueba_REE.xml"

      info_xml=lectura_SWE_D2_CapDoc_Prop_tree(path=strff)

      create_XML_CapDoc(path_output=pruebas, info_xml=info_xml, acept=True)

      #create_XML_CapDoc_by_Plantilla(path_input=strff, path_output=pruebas, info_xml=info_xml, acept=True)
      pass

   def test_read_idreport(self):
      read_idReport()
      read_nudosX()

   def test_read_excelCrack(self):
      lectura_excel_crack()


if __name__ == '__main__':
   unittest.main()
