import unittest
from Software.Entidades.lectura_ficheros import lectura_excel_crack
from Software.Core.lectura_xml import lectura_SWE_D2_CapDoc_Prop,InfoXML_to_Dataframe

class MyTestCase(unittest.TestCase):
   def test_lectura_xml_inputcoreso(self):
      strff=r"D:\TTC_CNE\Fich_Entrada\20190202_SWE_D2_CapDoc_Prop_REE.xml"

      clas_info_xml=lectura_SWE_D2_CapDoc_Prop(path=strff)
      df_infoXML=InfoXML_to_Dataframe(info_xml=clas_info_xml)
      pass



if __name__ == '__main__':
   unittest.main()
