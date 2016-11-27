##Create Contour Labels=name
##input_contours=vector
##input_label_guides=vector
##output_contours=output vector
##output_labels=output vector
##create_clipped_contours=boolean True
##smooth_contours=boolean False
##invert_labels=boolean False
##index_contour_modal=number 25
##contour_step=number 5
##start_buffer=number 20
##buffer_increment=number 10
##elevation_field_name=String elev
import math
import qgis
from qgis.core import *
from PyQt4.QtCore import *
def calcDist(p1x,p1y,p2x,p2y):
    dist = math.sqrt((p2x - p1x)**2 + (p2y - p1y)**2)
    return dist
version = qgis.utils.QGis.QGIS_VERSION.split('-')[0].split('.',2)
progress.setText("Running Contour Label creation for QGIS version "+str(qgis.utils.QGis.QGIS_VERSION.split('-')[0]))
if (smooth_contours):
    progress.setText("Smoothing contours")
    outputs_GRASSGENERALIZE_1=processing.runalg('grass7:v.generalize',input_contours,9,20,7,50,0.5,3,0,0,0,1,1,1,False,True,None,-1,0.0001,0,None)
    use_contours=outputs_GRASSGENERALIZE_1['output']
else:
    progress.setText("Using existing contours")
    use_contours=input_contours
progress.setText("Creating contour intersections")
outputs_QGISLINEINTERSECTIONS_1=processing.runalg('qgis:lineintersections',use_contours,input_label_guides,'ID','id',None)
progress.setText("Processing elevations")
outputs_QGISJOINATTRIBUTESTABLE_1=processing.runalg('qgis:joinattributestable', outputs_QGISLINEINTERSECTIONS_1['OUTPUT'],input_contours,'ID','ID',None)
outputs_QGISFIELDCALCULATOR_10=processing.runalg('qgis:fieldcalculator', outputs_QGISJOINATTRIBUTESTABLE_1['OUTPUT_LAYER'],'elevation',1,1.0,0.0,True,'"'+str(elevation_field_name)+'"',None)
outputs_QGISDELETECOLUMN_1=processing.runalg('qgis:deletecolumn',outputs_QGISFIELDCALCULATOR_10['OUTPUT_LAYER'],str(elevation_field_name),None)
outputs_QGISFIELDCALCULATOR_11=processing.runalg('qgis:fieldcalculator', outputs_QGISDELETECOLUMN_1['OUTPUT'],'elev',1,1.0,0.0,True,'"elevation"',None)
outputs_QGISDELETECOLUMN_2=processing.runalg('qgis:deletecolumn',outputs_QGISFIELDCALCULATOR_11['OUTPUT_LAYER'],'elevation',None)
outputs_QGISDELETECOLUMN_3=processing.runalg('qgis:deletecolumn',outputs_QGISDELETECOLUMN_2['OUTPUT'],'ID_2',None)
outputs_QGISFIELDCALCULATOR_7=processing.runalg('qgis:fieldcalculator', outputs_QGISDELETECOLUMN_3['OUTPUT'],'key',2,128.0,0.0,True,'concat("id_1",\'_\',"elev")',None)
progress.setText("Determining index contours")
outputs_QGISFIELDCALCULATOR_1=processing.runalg('qgis:fieldcalculator', outputs_QGISFIELDCALCULATOR_7['OUTPUT_LAYER'],'index',1,1.0,0.0,True,'"elev" % '+str(index_contour_modal)+' = 0',None)
progress.setText("Calculating label rotation")
outputs_QGISFIELDCALCULATOR_12=processing.runalg('qgis:fieldcalculator', outputs_QGISFIELDCALCULATOR_1['OUTPUT_LAYER'],'rot',0,6.0,3.0,True,'0',None)
outputs_QGISFIXEDDISTANCEBUFFER_3=processing.runalg('qgis:fixeddistancebuffer', outputs_QGISFIELDCALCULATOR_1['OUTPUT_LAYER'],2.0,5.0,False,None)
outputs_QGISINTERSECTION_2=processing.runalg('qgis:intersection', use_contours,outputs_QGISFIXEDDISTANCEBUFFER_3['OUTPUT'],None)
outputs_QGISFIELDCALCULATOR_2=processing.runalg('qgis:fieldcalculator', outputs_QGISINTERSECTION_2['OUTPUT'],'sint',2,128.0,0.0,True,'geom_to_wkt(start_point($geometry))',None)
outputs_QGISFIELDCALCULATOR_3=processing.runalg('qgis:fieldcalculator', outputs_QGISFIELDCALCULATOR_2['OUTPUT_LAYER'],'eint',2,128.0,0.0,True,'geom_to_wkt(end_point($geometry))',None)
if (invert_labels):
    deg = 270
else:
    deg = 90
outputs_QGISFIELDCALCULATOR_5=processing.runalg('qgis:fieldcalculator', outputs_QGISFIELDCALCULATOR_3['OUTPUT_LAYER'],'rot',0,6.0,3.0,True,str(deg)+'-((atan((x(geom_from_wkt("sint"))-x(geom_from_wkt("eint")))/(y(geom_from_wkt("sint"))-y(geom_from_wkt("eint")))))*180/3.14159+(180*(((y(geom_from_wkt("sint"))-y(geom_from_wkt("eint")))<0)+(((x(geom_from_wkt("sint"))-x(geom_from_wkt("eint")))<0 AND (y(geom_from_wkt("sint"))-y(geom_from_wkt("eint")))>0)*2))))',None)
progress.setText("Determining contours to label")
rlayer = QgsVectorLayer(outputs_QGISFIELDCALCULATOR_5['OUTPUT_LAYER'], 'rlayer', 'ogr')
tlayer = QgsVectorLayer(outputs_QGISFIELDCALCULATOR_12['OUTPUT_LAYER'], 'tlayer', 'ogr')
dshort =start_buffer
dmid =start_buffer*2
dlong = start_buffer*3
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
        if (t['key'] == str(f['id_1'])+'_'+str(f['elev']+contour_step)):
            fup = t
            break
        else:
            fup = -99
    t = None
    for t in processing.features(tlayer):
        if (t['key'] == str(f['id_1'])+'_'+str(f['elev']-contour_step)):
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
        if ((distu >= dlong and distd >= dlong) or (distu >= dlong and fdown == -99) or (distd >= dlong and fup == -99)):
            change = 1
        elif ((distu >= dmid and fui == 0 and distd >= dmid and fdi == 0) or (distu >= dmid and fui == 0 and fdown == -99) or (distd >= dmid and fdi == 0 and fup == -99)):
            change = 1
    tlayer.changeAttributeValue(f.id(), new_field_index, change)
tlayer.commitChanges()
tlayer.startEditing()
for f in processing.features(tlayer):
    t = None
    for t in processing.features(tlayer):
        if (t['key'] == str(f['id_1'])+'_'+str(f['elev']+contour_step)):
            fup = t
            break
        else:
            fup = -99
    t = None
    for t in processing.features(tlayer):
        if (t['key'] == str(f['id_1'])+'_'+str(f['elev']-contour_step)):
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
        if (distu > dshort and ful == 0 and distd > dshort and fdl == 0):
            change = 1
        elif (distu > dshort and ful == 0 and distd >= dlong):
            change = 1
        elif (distd > dshort and fdl == 0 and distu >= dlong):
            change = 1
        tlayer.changeAttributeValue(f.id(), new_field_index, change)
tlayer.commitChanges()
outputs_QGISFIELDCALCULATOR_8=processing.runalg('qgis:fieldcalculator', outputs_QGISFIELDCALCULATOR_12['OUTPUT_LAYER'],'buffer',1,3.0,0.0,True,'('+str(start_buffer)+' + ((length(to_string( "elev"))-1) * '+str(buffer_increment)+'))',None)
if (create_clipped_contours):
    progress.setText("Creating clipped contours")
    outputs_QGISEXTRACTBYATTRIBUTE_1=processing.runalg('qgis:extractbyattribute', outputs_QGISFIELDCALCULATOR_8['OUTPUT_LAYER'],'label',0,'1',None)
    outputs_QGISFIXEDDISTANCEBUFFER_1=processing.runalg('qgis:fixeddistancebuffer', outputs_QGISEXTRACTBYATTRIBUTE_1['OUTPUT'],2.0,5.0,False,None)
    outputs_QGISVARIABLEDISTANCEBUFFER_1=processing.runalg('qgis:variabledistancebuffer', outputs_QGISEXTRACTBYATTRIBUTE_1['OUTPUT'],'buffer',5.0,False,None)
    outputs_QGISINTERSECTION_1=processing.runalg('qgis:intersection', use_contours,outputs_QGISVARIABLEDISTANCEBUFFER_1['OUTPUT'],None)
    outputs_QGISMULTIPARTTOSINGLEPARTS_1=processing.runalg('qgis:multiparttosingleparts', outputs_QGISINTERSECTION_1['OUTPUT'],None)
    if (int(version[0]) == 2 and int(version[1]) == 14):
        outputs_QGISEXTRACTBYLOCATION_1=processing.runalg('qgis:extractbylocation', outputs_QGISMULTIPARTTOSINGLEPARTS_1['OUTPUT'],outputs_QGISFIXEDDISTANCEBUFFER_1['OUTPUT'],['intersects','crosses'],None)
    elif (int(version[0]) == 2 and int(version[1]) == 16):
        outputs_QGISEXTRACTBYLOCATION_1=processing.runalg('qgis:extractbylocation', outputs_QGISMULTIPARTTOSINGLEPARTS_1['OUTPUT'],outputs_QGISFIXEDDISTANCEBUFFER_1['OUTPUT'],['intersects','crosses'],1.0,None)
    outputs_QGISFIXEDDISTANCEBUFFER_2=processing.runalg('qgis:fixeddistancebuffer', outputs_QGISEXTRACTBYLOCATION_1['OUTPUT'],2.0,5.0,False,None)
    progress.setText("Returning final clipped contours")
    if (int(version[0]) == 2 and int(version[1]) == 14):
        outputs_QGISDIFFERENCE_1=processing.runalg('qgis:difference',use_contours,outputs_QGISFIXEDDISTANCEBUFFER_2['OUTPUT'],output_contours)
    elif (int(version[0]) == 2 and int(version[1]) == 16):
        outputs_QGISDIFFERENCE_1=processing.runalg('qgis:difference',use_contours,outputs_QGISFIXEDDISTANCEBUFFER_2['OUTPUT'],False,output_contours)
else:
    output_contours = input_contours
progress.setText("Cleaning output layers.")
progress.setText("Returning labels")
outputs_QGISDELETECOLUMN_4=processing.runalg('qgis:deletecolumn',outputs_QGISFIELDCALCULATOR_8['OUTPUT_LAYER'],'buffer',None)
outputs_QGISDELETECOLUMN_5=processing.runalg('qgis:deletecolumn',outputs_QGISDELETECOLUMN_4['OUTPUT'],'ID',None)
outputs_QGISDELETECOLUMN_6=processing.runalg('qgis:deletecolumn',outputs_QGISDELETECOLUMN_5['OUTPUT'],'ID_1',output_labels)
progress.setText("All done.")
