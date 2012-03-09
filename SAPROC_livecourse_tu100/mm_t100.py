# DEPENDENCIES
## We're going to load files in from a course related directory
import os
## Quick hack approach - use lxml parser to parse SA XML files
from lxml import etree
# We may find it handy to generate timestamps...
import time
#Useful for generating simple report files
import csv

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
		print 'Page',page
		#Week 0 and Week 10 are special cases and don't follow the standard teaching week layout
		if page!='week0.xml' and page!='week10.xml':
			tree = etree.parse('/'.join([SA_XMLfiledir,page]))
			courseRoot = tree.getroot()
			parsePage(courseRoot,root)
	return mm

#Could we make a secondary product out of glossary items?
def glossaryItems(courseroot,root):
	pass

def learningOutcomes(courseRoot,root):
	mmlos=etree.SubElement(root,"node")
	mmlos.set("TEXT","Learning Outcomes")
	mmlos.set("FOLDED","true")
	
	los=courseRoot.findall('.//Unit/LearningOutcomes/LearningOutcome')
	for lo in los:
		mmsession=etree.SubElement(mmlos,"node")
		mmsession.set("TEXT",flatten(lo))

def parsePage(courseRoot,root):
	unitTitle=courseRoot.find('.//ItemTitle')

	mmweek=etree.SubElement(root,"node")
	mmweek.set("TEXT",flatten(unitTitle))
	mmweek.set("FOLDED","true")

	learningOutcomes(courseRoot,mmweek)
	
	sessions=courseRoot.findall('.//Unit/Session')
	for session in sessions:
		title=flatten(session.find('.//Title'))
		mmsession=etree.SubElement(mmweek,"node")
		mmsession.set("TEXT",title)
		mmsession.set("FOLDED","true")
		subsessions=session.findall('.//Section')
		for subsession in subsessions:
			heading=subsession.find('.//Title')
			if heading !=None:
				title=flatten(heading)
				mmsubsession=etree.SubElement(mmsession,"node")
				mmsubsession.set("TEXT",title)
				mmsubsession.set("FOLDED","true")

	courseCode=flatten(courseRoot.find('.//CourseCode'))
	glossary=courseRoot.findall('.//BackMatter/Glossary/GlossaryItem')
	fo=open('reports/glossary.txt','wb+')
	writer=csv.writer(fo)
	writer.writerow(['courseCode','term','definition'])
	for glossitem in glossary:
		term=flatten(glossitem.find('Term'))
		definition=flatten(glossitem.find('Definition'))
		print courseCode,term,definition
		#fudge the output for now to ignore non-ascii characters
		writer.writerow([courseCode.encode('ascii','ignore'),term.encode('ascii','ignore'),definition.encode('ascii','ignore')])
	fo.close()
	
	#Grab figures
	figures=courseRoot.findall('.//Figure')
	fo=open('reports/figures.txt','wb+')
	writer=csv.writer(fo)
	writer.writerow(['xsrc','caption','desc'])
	#Note that acknowledgements to figures are provided at the end of the XML file with only informal free text/figure number identifers available for associating a particular acknowledgement/copyright assignment with a given image. It would be so much neater if this could be bundled up with the figure itself, or if the figure and the acknowledgement could share the same unique identifier?
	for figure in figures:
		img=figure.find('Image')
		src=img.get('src')
		xsrc=img.get('x_imagesrc')
		caption=flatten(figure.find('Caption'))
		#in desc, need to find a way of stripping <Number> element from start of description
		desc=flatten(figure.find('Description'))
		print xsrc,caption,desc
		writer.writerow([courseCode.encode('ascii','ignore'),xsrc,caption.encode('ascii','ignore'),desc.encode('ascii','ignore')])
	fo.close()


mm=freemindRoot('tu100_1.xml')
#print etree.tostring(mm, pretty_print=True)
xmlFileSave('reports/test_tu100_full.mm',mm)