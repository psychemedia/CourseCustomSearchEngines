# DEPENDENCIES
## We're going to load files in from a course related directory
import os
## Quick hack approach - use lxml parser to parse SA XML files
from lxml import etree
# We may find it handy to generate timestamps...
import time


# CONFIGURATION

## The directory the course XML files are in (separate directory for each course for now) 
SA_XMLfiledir='data'
## We can get copies of the XML versions of Structured Authoring documents
## that are rendered in the VLE by adding &content=1 to the end of the URL
## [via Colin Chambers]
## eg http://learn.open.ac.uk/mod/oucontent/view.php?id=526433&content=1



# UTILITIES

#lxml flatten routine - grab text from across subelements
#via http://stackoverflow.com/questions/5757201/help-or-advice-me-get-started-with-lxml/5899005#5899005
def flatten(el):           
    result = [ (el.text or "") ]
    for sel in el:
        result.append(flatten(sel))
        result.append(sel.tail or "")
    return "".join(result)

#Quick and dirty handler for saving XML trees as files
def xmlFileSave(fn,xml):
	# Output
	txt = etree.tostring(xml, pretty_print=True)
	#print txt
	fout=open(fn,'wb+')
	#fout.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
	fout.write(txt)
	fout.close()


#GENERATE A FREEMIND MINDMAP FROM A SINGLE T151 SA DOCUMENT
## The structure of the T151 course lends itself to a mindmap/tree style visualisation
## Essentially what we are doing here is recreating an outline view of the course that was originally used in the course design phase
def freemindRoot(page):
	tree = etree.parse('/'.join([SA_XMLfiledir,page]))
	courseRoot = tree.getroot()
	mm=etree.Element("map")
	mm.set("version", "0.9.0")
	root=etree.SubElement(mm,"node")
	root.set("CREATED",str(int(time.time())))
	root.set("STYLE","fork")
	#We probably need to bear in mind escaping the text strings?
	#courseRoot: The course title is not represented consistently in the T151 SA docs, so we need to flatten it
	title=flatten(courseRoot.find('CourseTitle'))
	root.set("TEXT",title)
	
	## Grab a listing of the SA files in the target directory
	listing = os.listdir(SA_XMLfiledir)

	#For each SA doc, we need to handle it separately
	for page in listing:
		print page
		#Week 0 and Week 10 are special cases and don't follow the standard teaching week layout
		if page!='week0.xml' and page!='week10.xml':
			tree = etree.parse('/'.join([SA_XMLfiledir,page]))
			courseRoot = tree.getroot()
			parsePage(courseRoot,root)
	return mm


def parsePage(courseRoot,root):
	unitTitle=courseRoot.find('.//Unit/UnitTitle')

	mmweek=etree.SubElement(root,"node")
	mmweek.set("TEXT",flatten(unitTitle))
	mmweek.set("FOLDED","true")

	sessions=courseRoot.findall('.//Unit/Session')
	for session in sessions:
		title=flatten(session.find('.//Title'))
		mmsession=etree.SubElement(mmweek,"node")
		mmsession.set("TEXT",title)
		mmsession.set("FOLDED","true")
		subsessions=session.findall('.//InternalSection')
		for subsession in subsessions:
			heading=subsession.find('.//Heading')
			if heading !=None:
				title=flatten(heading)
				mmsubsession=etree.SubElement(mmsession,"node")
				mmsubsession.set("TEXT",title)
				mmsubsession.set("FOLDED","true")


mm=freemindRoot('week2.xml')
print etree.tostring(mm, pretty_print=True)
xmlFileSave('reports/test_t184_full.mm',mm)