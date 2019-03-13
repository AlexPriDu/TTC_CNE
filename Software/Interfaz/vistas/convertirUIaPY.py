# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        convertitUIaPY
# Purpose:     Convertir .ui a .py
#
# Author:      Carlos Martin
#
# Created:     03/11/2017
# Copyright:   (c) Aeroengy 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys
import PySide
from pysideuic import compileUi
from Software.Interfaz import vistas
import os


def set_rutas():
    """
    Para inciar en mapeo entre los archivos ui y los py
    :return: un listado de este mapeo
    :rtype list of Archivos
    """

    class Archivos(object):
        def __init__(self, RUTA_PY=None, RUTA_UI=None,convertir=True):
            self.RUTA_PY = RUTA_PY
            self.RUTA_UI = RUTA_UI
            self.convertir=convertir #Borrado logico


    list_rutas=[]

    vist_path=os.path.dirname(vistas.__file__)

    list_rutas.append(Archivos(RUTA_PY=os.path.join(vist_path,'MainWindow.py'),
                       RUTA_UI=os.path.join(vist_path,'xml_coreso.ui'), convertir=True))


    return list_rutas




def main():
    try:
        list_rutas=set_rutas()
        list_rutas=filter(lambda x: x.convertir,list_rutas)

        for ruta in list_rutas:

            rutaUI=ruta.RUTA_UI
            rutaPyhtonSalida=ruta.RUTA_PY
            pyfile = open(rutaPyhtonSalida, 'w')

            compileUi(rutaUI, pyfile, False, 4, False)

            pyfile.close()

    except Exception as e:
        print e

if __name__ == '__main__':
    main()
