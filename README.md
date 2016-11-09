# Contour-Labels

## Introduction
Using QGIS 2.14.8 LTE or 2.16.1 (various versions have slight nuances in the running of processing algorithms running from within python), create a new script using the content of the create_contour_labels.py script in the repository.
The script is initially designed to be run against data layers in BNG (EPSG:27700) format.

## Quick start steps
1. Create contour layer.

  Ideally from DEM using QGIS' inbuilt contour extractor. For other sources ensure the isolines follow a common pattern - i.e. uphill always on same side. The contour label processing script is developed for a default 5m contour interval, though this can be changed by the user.
  
  Alternatively use the [**contours.shp** and associated files][os opendata] (1) from the **test** folder in the repository.
2. Create label guides layer.

  This is a polyline vector layer created manually by the user. Simply draw lines for each set of ascending/descending labels. Make sure to not cross previously crossed contours in any individual line and only cross contours where you want to have a label displayed later (pending some clever math from the processing script). Give each guide a unique numeric id, ideally starting at 1.
  
  Alternatively use the **guides.shp** and associated files from the **test** folder in the repository.
3. Run the **create_contour_labels.py** script from the QGIS user scripts toolbox using the inputs you just created.

  A note on the various options available:
  - **input contours**: The contour layer you created/obtained in step 1.
  - **input label guides**: The guide layer you created in step 2.
  - **create clipped contours**: If you only want labels that are rotated, then deselect this. If selected the algorithm will produce a clipped set of contours to make space for the labels. If unsure run both separately and decide yourself.
  - **invert labels**: If labels are rotated 180 degrees in the wrong direction (upside down), select this and run the processing again.
  - **index contour modal**: Interval of index contours (usually displayed different for emphasis). Default is 25. OS 25k maps use 50m index intervals and vary the actual contour interval between 5m and 10m depending on the terrain in an area.
  - **contour step**: The actual contour interval used. This is used to create the intelligent labelling based on distance to neighbouring contours. Default is 5, adjust for your input contours.
  - **start buffer**: Depending on your style for the labels you may have to adjust this value to ensure enough space for them and the clips in the final contour output (if selected). The default is designed to work with the provided stylesheets.
  - **buffer increment**: Depending on your style for the labels you may have to adjust this value to ensure enough space for them and the clips in the final contour output (if selected). The increment is used for the length of the clip and results in _(start_buffer + (label.length()-1)*buffer_increment)_
  - **output contours**: The file to save the clipped output contours to. Temp file by default.
  - **output labels**: The file to save the new labels to. Temp file by default.

4. Apply the QML style sheets from the repository to see the default effect and identify how the labelling is managed. Default styling and settings are for a 5m interval with index contours every 25m to view at a 1:25k scale.

## References
(1): [Contains OS data © Crown copyright and database right (2016).][os opendata]

[os opendata]: https://www.ordnancesurvey.co.uk/opendatadownload/products.html
