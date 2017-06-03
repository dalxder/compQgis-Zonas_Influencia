# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InfluenceZone
                                 A QGIS plugin
 Crea poligono del area de influencia de una polilinea, a la derecha, izquierda o, ambos lados
                             -------------------
        begin                : 2017-06-03
        copyright            : (C) 2017 by dalxder
        email                : dalxder@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load InfluenceZone class from file InfluenceZone.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .infl_zone import InfluenceZone
    return InfluenceZone(iface)
