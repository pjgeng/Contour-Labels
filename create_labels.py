##Create Contour Labels=name
##VECTORLAYER_CONTOURS=vector
##VECTORLAYER_GUIDES=vector
##contours=output vector
##labels=output vector
import math
import qgis
from qgis.core import *
from PyQt4.QtCore import *
def calcDist(p1x,p1y,p2x,p2y):
    dist = math.sqrt((p2x - p1x)**2 + (p2y - p1y)**2)
    return dist
outputs_QGISLINEINTERSECTIONS_1=processing.runalg('qgis:lineintersections', VECTORLAYER_CONTOURS,VECTORLAYER_GUIDES,'ID','id',None)
outputs_QGISJOINATTRIBUTESTABLE_1=processing.runalg('qgis:joinattributestable', outputs_QGISLINEINTERSECTIONS_1['OUTPUT'],VECTORLAYER_CONTOURS,'ID','ID',None)
outputs_QGISFIELDCALCULATOR_10=processing.runalg('qgis:fieldcalculator', outputs_QGISJOINATTRIBUTESTABLE_1['OUTPUT_LAYER'],'elevation',1,1.0,0.0,True,'"elev"',None)
outputs_QGISDELETECOLUMN_1=processing.runalg('qgis:deletecolumn',outputs_QGISFIELDCALCULATOR_10['OUTPUT_LAYER'],'elev',None)
outputs_QGISFIELDCALCULATOR_11=processing.runalg('qgis:fieldcalculator', outputs_QGISDELETECOLUMN_1['OUTPUT'],'elev',1,1.0,0.0,True,'"elevation"',None)
outputs_QGISDELETECOLUMN_2=processing.runalg('qgis:deletecolumn',outputs_QGISFIELDCALCULATOR_11['OUTPUT_LAYER'],'elevation',None)
outputs_QGISDELETECOLUMN_3=processing.runalg('qgis:deletecolumn',outputs_QGISDELETECOLUMN_2['OUTPUT'],'ID_2',None)
outputs_QGISFIELDCALCULATOR_7=processing.runalg('qgis:fieldcalculator', outputs_QGISDELETECOLUMN_3['OUTPUT'],'key',2,128.0,0.0,True,'concat("id_1",\'_\',"elev")',None)
outputs_QGISFIELDCALCULATOR_1=processing.runalg('qgis:fieldcalculator', outputs_QGISFIELDCALCULATOR_7['OUTPUT_LAYER'],'index',1,1.0,0.0,True,'"elev" % 25 = 0',None)
outputs_QGISFIELDCALCULATOR_12=processing.runalg('qgis:fieldcalculator', outputs_QGISFIELDCALCULATOR_1['OUTPUT_LAYER'],'rot',0,6.0,3.0,True,'0',None)
outputs_QGISFIXEDDISTANCEBUFFER_3=processing.runalg('qgis:fixeddistancebuffer', outputs_QGISFIELDCALCULATOR_1['OUTPUT_LAYER'],2.0,5.0,False,None)
outputs_QGISINTERSECTION_2=processing.runalg('qgis:intersection', VECTORLAYER_CONTOURS,outputs_QGISFIXEDDISTANCEBUFFER_3['OUTPUT'],None)
outputs_QGISFIELDCALCULATOR_2=processing.runalg('qgis:fieldcalculator', outputs_QGISINTERSECTION_2['OUTPUT'],'sint',2,128.0,0.0,True,'geom_to_wkt(start_point($geometry))',None)
outputs_QGISFIELDCALCULATOR_3=processing.runalg('qgis:fieldcalculator', outputs_QGISFIELDCALCULATOR_2['OUTPUT_LAYER'],'eint',2,128.0,0.0,True,'geom_to_wkt(end_point($geometry))',None)
outputs_QGISFIELDCALCULATOR_5=processing.runalg('qgis:fieldcalculator', outputs_QGISFIELDCALCULATOR_3['OUTPUT_LAYER'],'rot',0,6.0,3.0,True,'90-((atan((x(geom_from_wkt("sint"))-x(geom_from_wkt("eint")))/(y(geom_from_wkt("sint"))-y(geom_from_wkt("eint")))))*180/3.14159+(180*(((y(geom_from_wkt("sint"))-y(geom_from_wkt("eint")))<0)+(((x(geom_from_wkt("sint"))-x(geom_from_wkt("eint")))<0 AND (y(geom_from_wkt("sint"))-y(geom_from_wkt("eint")))>0)*2))))',None)
rlayer = QgsVectorLayer(outputs_QGISFIELDCALCULATOR_5['OUTPUT_LAYER'], 'rlayer', 'ogr')
tlayer = QgsVectorLayer(outputs_QGISFIELDCALCULATOR_12['OUTPUT_LAYER'], 'tlayer', 'ogr')
if not tlayer.isValid():
    progress.setText("Layer failed to load!")
    exit(0)
if not rlayer.isValid():
    progress.setText("Layer failed to load!")
    exit(0)
tlayer.dataProvider().addAttributes([QgsField("label", QVariant.Int)])
tlayer.updateFields()
new_field_index = tlayer.fieldNameIndex('label')
rot_index = tlayer.fieldNameIndex('rot')
tlayer.startEditing()
for f in processing.features(tlayer):
    tlayer.changeAttributeValue(f.id(), new_field_index, 0)
    for t in processing.features(rlayer):
        if (f['key'] == t['key']):
            tlayer.changeAttributeValue(f.id(), rot_index, t['rot'])
tlayer.commitChanges()
tlayer.startEditing()
for f in processing.features(tlayer):
    t = None
    for t in processing.features(tlayer):
        if (t['key'] == str(f['id_1'])+'_'+str(f['elev']+5)):
            fup = t
            break
        else:
            fup = -99
    t = None
    for t in processing.features(tlayer):
        if (t['key'] == str(f['id_1'])+'_'+str(f['elev']-5)):
            fdown = t
            break
        else:
            fdown = -99
    change = 0
    if (f['index'] == 1):
        change = 1
    else:
        if (fdown != -99):
            distd = calcDist(f.geometry().asPoint().x(),f.geometry().asPoint().y(),fdown.geometry().asPoint().x(),fdown.geometry().asPoint().y())
            fdl = fdown['label']
            fdi = fdown['index']
        else:
            distd = 0
            fdl = 0
            fdi = 0
        if (fup != -99):
            distu = calcDist(f.geometry().asPoint().x(),f.geometry().asPoint().y(),fup.geometry().asPoint().x(),fup.geometry().asPoint().y())
            ful = fup['label']
            fui = fup['index']
        else:
            distu = 0
            ful = 0
            fui = 0
        if ((distu >= 60 and distd >= 60) or (distu >= 60 and fdown == -99) or (distd >= 60 and fup == -99)):
            change = 1
        elif ((distu >= 40 and fui == 0 and distd >= 40 and fdi == 0) or (distu >= 40 and fui == 0 and fdown == -99) or (distd >= 40 and fdi == 0 and fup == -99)):
            change = 1
    tlayer.changeAttributeValue(f.id(), new_field_index, change)
tlayer.commitChanges()
tlayer.startEditing()
for f in processing.features(tlayer):
    t = None
    for t in processing.features(tlayer):
        if (t['key'] == str(f['id_1'])+'_'+str(f['elev']+5)):
            fup = t
            break
        else:
            fup = -99
    t = None
    for t in processing.features(tlayer):
        if (t['key'] == str(f['id_1'])+'_'+str(f['elev']-5)):
            fdown = t
            break
        else:
            fdown = -99
    if (f['label'] == 1):
        continue
    else:
        change = 0
        if (fdown != -99):
            distd = calcDist(f.geometry().asPoint().x(),f.geometry().asPoint().y(),fdown.geometry().asPoint().x(),fdown.geometry().asPoint().y())
            fdl = fdown['label']
            fdi = fdown['index']
        else:
            distd = 0
            fdl = 0
            fdi = 0
        if (fup != -99):
            distu = calcDist(f.geometry().asPoint().x(),f.geometry().asPoint().y(),fup.geometry().asPoint().x(),fup.geometry().asPoint().y())
            ful = fup['label']
            fui = fup['index']
        else:
            distu = 0
            ful = 0
            fui = 0
        if (distu > 20 and ful == 0 and distd > 20 and fdl == 0):
            change = 1
        elif (distu > 20 and ful == 0 and distd >= 60):
            change = 1
        elif (distd > 20 and fdl == 0 and distu >= 60):
            change = 1
        tlayer.changeAttributeValue(f.id(), new_field_index, change)
tlayer.commitChanges()
outputs_QGISFIELDCALCULATOR_8=processing.runalg('qgis:fieldcalculator', outputs_QGISFIELDCALCULATOR_12['OUTPUT_LAYER'],'buffer',1,3.0,0.0,True,'(20 + ((length(to_string( "elev"))-1) * 10))',labels)
outputs_QGISEXTRACTBYATTRIBUTE_1=processing.runalg('qgis:extractbyattribute', outputs_QGISFIELDCALCULATOR_8['OUTPUT_LAYER'],'label',0,'1',None)
outputs_QGISFIXEDDISTANCEBUFFER_1=processing.runalg('qgis:fixeddistancebuffer', outputs_QGISEXTRACTBYATTRIBUTE_1['OUTPUT'],2.0,5.0,False,None)
outputs_QGISVARIABLEDISTANCEBUFFER_1=processing.runalg('qgis:variabledistancebuffer', outputs_QGISEXTRACTBYATTRIBUTE_1['OUTPUT'],'buffer',5.0,False,None)
outputs_QGISINTERSECTION_1=processing.runalg('qgis:intersection', VECTORLAYER_CONTOURS,outputs_QGISVARIABLEDISTANCEBUFFER_1['OUTPUT'],None)
outputs_QGISMULTIPARTTOSINGLEPARTS_1=processing.runalg('qgis:multiparttosingleparts', outputs_QGISINTERSECTION_1['OUTPUT'],None)
outputs_QGISEXTRACTBYLOCATION_1=processing.runalg('qgis:extractbylocation', outputs_QGISMULTIPARTTOSINGLEPARTS_1['OUTPUT'],outputs_QGISFIXEDDISTANCEBUFFER_1['OUTPUT'],['intersects','crosses'],None)
outputs_QGISFIXEDDISTANCEBUFFER_2=processing.runalg('qgis:fixeddistancebuffer', outputs_QGISEXTRACTBYLOCATION_1['OUTPUT'],2.0,5.0,False,None)
outputs_QGISDIFFERENCE_1=processing.runalg('qgis:difference', VECTORLAYER_CONTOURS,outputs_QGISFIXEDDISTANCEBUFFER_2['OUTPUT'],contours)
