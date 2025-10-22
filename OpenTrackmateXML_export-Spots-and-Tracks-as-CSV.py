# Essentially a batched version of macros found on https://imagej.net/plugins/trackmate/scripting/scripting

#@ File (style = "directory", label = "Input directory with TrackMate XML files") srcDir
#@ File (style = "directory", label = "Output directory for TrackMate CSV files") dstDir
#@ String  (label = "File extension", value=".xml") ext
#@ String  (label = "File name contains", value = "") containString

import os, sys
from fiji.plugin.trackmate.visualization.table import TrackTableView
from fiji.plugin.trackmate.io import TmXmlReader
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate.gui.displaysettings import DisplaySettings
import java.io.File

# Necessary to avoid errors with UTF8 chars generated in 
# TrackMate that will mess with Fiji Jython.
reload(sys)
sys.setdefaultencoding('utf-8')

def run(srcDir, dstDir):
	srcDir = srcDir.getAbsolutePath()
	dstDir = dstDir.getAbsolutePath()
	for root, directories, filenames in os.walk(srcDir):
		filenames.sort();
	for filename in filenames:
		# Check for file extension
		if not filename.endswith(ext):
			continue
		# Check for file name pattern
		if containString not in filename:
			continue
		process(srcDir, dstDir, root, filename)
	print "done"

def process(srcDir, dstDir, currentDir, fileName):
	# --- Prepare filenames and paths --- #
	# Create Java File object for XML file
	xmlfile = java.io.File( os.path.join(srcDir, fileName) )
	fileNameWithoutExt = fileName.rsplit(".xml")[0]
	
	spots_csv_name  = fileNameWithoutExt + "_spots.csv"
	tracks_csv_name = fileNameWithoutExt + "_tracks.csv"
	spots_csv_file  = os.path.join(dstDir, spots_csv_name)
	tracks_csv_file = os.path.join(dstDir, tracks_csv_name)
	
	# Create Java File objects for csv pathnames
	outSpotsPath = java.io.File(spots_csv_file)
	outTrackPath = java.io.File(tracks_csv_file)
	
	# --- Open the TrackMate XML file --- #
	print xmlfile
	reader = TmXmlReader(xmlfile)
	
	if not reader.isReadingOk():
		sys.exit( reader.getErrorMessage() )

	# This will return a fully working model, with everything
	# stored in the file. Missing fields (e.g. tracks) will be
	# null or None in python
	model = reader.getModel()
	
	sm = SelectionModel(model)
	ds = DisplaySettings()
	
	# --- Get and save spot and track statistics --- #
	trackTableView = TrackTableView(model, sm, ds)
	
	trackTableView.getSpotTable().exportToCsv(outSpotsPath)
	trackTableView.getTrackTable().exportToCsv(outTrackPath)

run(srcDir, dstDir)