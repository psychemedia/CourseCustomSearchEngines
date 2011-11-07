# ESTEEM PROJECT (GOOGLE CUSTOM COURSE SEARCH ENGINES) DELIVERABLE
## Tony Hirst, a.j.hirst, Dept of Communication and Systems

## A script to generate Google Custom Search Engine Annotations file
## from external pointing links contained within OU VLE course webpages

## This script starts to raise and explore some of the issues involved as we scrape links from across a course.
## For example:
### how should we handle duplicate links?
### are we indexing pages, domains, or both in the CSE?
### should different SA docs be allowed to map on to different tabs in the CSE? How might we manage this?
### should we try to remember where each link came from?
### do we want to use different weights in the CSE for different links? How might we determine such weights?
### how should we handle links that point to eg libezproxified DOIs?

## The script in part relies on conventions in markup that are used to express the standardised format of the T151 course model.
## In particular, study weeks contain topic explorations, each of which has a common structure that we draw on:
### - questions used to frame a topic exploration
### - resources organised by type to support the topic exploration

##FURTHER IDEAS
### Add links shared via t151 tag on delicious to the CSE in a 'Student Recommended' tab 
### Add in links shared via a Google Reader feed to the CSE

# DEPENDENCIES
## We're going to load files in from a course related directory
import os
## Quick hack approach - use lxml parser to parse SA XML files
from lxml import etree
## When we test URLs, we might as well be able to parse them comprehensively
from urlparse import urlparse
# We may find it handy to generate timestamps...
import time

#CONFIGURATION
## There's a little bit of config information we need

## The label of the custom search engine we want the annotations file to apply to
cselabel="_cse_bf8jg9spayc"

## The directory the course XML files are in (separate directory for each course for now) 
SA_XMLfiledir='data/'
## We can get copies of the XML versions of Structured Authoring documents
## that are rendered in the VLE by adding &content=1 to the end of the URL
## [via Colin Chambers]
## eg http://learn.open.ac.uk/mod/oucontent/view.php?id=526433&content=1

#BUILD A LIST OF EXTERNAL LINKS
# We may get the same link referenced in several places, so build up a list of unique links
# At the moment, I'll key the dict with the URL, but an MD5 hash may be more convenient?
# Would it also be worth defining a link class to structure the link data?
externalLinks={}

#Maintain a list of unique links we have seen, along with a list of link text descriptors for each unique link
def addExternalLink(linkslist,link):
	url = link.get('href')
	desc = link.text
	if url in linkslist:
		linkslist[url]['desc'].append(desc)
		# Rather than increment a counter explicitly, base the number of occurrences of the link on the number of link text descriptions we have captured. If we were using a class, we could use a method to return the link occurrence on this basis.
		linkslist[url]['count']=len(linkslist[url]['desc'])
	else:
		linkslist[url]={'count':1,'desc':[desc]}
	return linkslist

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
	fout.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
	fout.write(txt)
	fout.close()


#GENERATE A FREEMIND MINDMAP FROM A SINGLE T151 SA DOCUMENT
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
	
	#For each SA doc, we need to handle it separately
	for page in listing:
		print page
		#Week 0 and Week 10 are special cases and don't follow the standard teaching week layout
		if page!='t151Week0.xml' and page!='t151Week10.xml':
			tree = etree.parse('/'.join([SA_XMLfiledir,page]))
			courseRoot = tree.getroot()
			generateFreeMindLinksMapFromDoc(courseRoot,root)
	return mm

def generateFreeMindLinksMapFromDoc(courseRoot,root):

	weektitle=courseRoot.find('.//Unit/Session/Title')
	week=courseRoot.find('.//Unit/Session')
	
	mmweek=etree.SubElement(root,"node")
	mmweek.set("TEXT",flatten(weektitle))
	mmweek.set("FOLDED","true")
	print 'looking for topics'
	topics=week.findall('.//Section')
	#Weeks are generally split into two topic explorations per week.
	#Handle each topic exploration separately
	for topic in topics:
		print 'trying topics'
		title=flatten(topic.find('.//Title'))
		if title.startswith('Topic'):
			resources=etree.SubElement(mmweek,"node")
			resources.set("TEXT",title)
			resources.set("FOLDED","true")
			handleMMquestions(topic,resources)
			handleMMlinks(topic,resources)

def handleMMquestions(courseRoot,resources):
	qsection = courseRoot.find(".//SubSection")
	title=flatten(qsection[0])
	if title.startswith('Questions'):
		currResource=etree.SubElement(resources,"node")
		currResource.set("TEXT","Questions")
		currResource.set("FOLDED","true")
		qqsection=qsection.find('NumberedList')
		print qqsection
		if qqsection!=None:
			for question in qqsection.iter('ListItem'):
				qResource=etree.SubElement(currResource,"node")
				qtext=flatten(question)
				qResource.set("TEXT",qtext)
	
def handleMMlinks(courseRoot,resources):
	#Find the resources section; we're relying on all sorts of conventions here so this is likely to be brittle
	resourceLists = courseRoot.findall(".//InternalSection")

	for rl in resourceLists:
		title=flatten(rl[0])
		print title
		currResource=etree.SubElement(resources,"node")
		currResource.set("TEXT",title)
		currResource.set("FOLDED","true")
		links=rl.findall('.//ListItem/a')
		for link in links:
			linkResource=etree.SubElement(currResource,"node")
			linkResource.set("LINK",link.get('href'))
			#Once again, the SA doc is a mess. Sometimes there's a font tag, sometimes there isn't
			linktext=flatten(link)
			linkResource.set("TEXT",linktext)
	#txt = etree.tostring(mm, pretty_print=True)
	#print txt


#ADD IN LINKS TO THE CSE FROM AN EXTERNAL FEED
def grabFeedLinks(feed):
	pass

#GENERATE THE GOOGLE CSE ANNOTATIONS FILE

## For each link in a list, add it to the annotations tree
def addLinksToAnnotationsXML(annotations,links,cselabel):
	for url in links:
		print 'Handling',url
		#We only want the external links
		netloc=urlparse(url)[1]
		print '.........',netloc
		# There is a variety of links off the open.ac.uk domain, including libezproxy links
		# Maybe need to consider ways of handling these? Eg for libezproxy, should we maybe try to get a public abstract
		# page for the corresponding article added to the CSE index?
		if netloc.find('open.ac.uk')<0:
			print '... and using it...'
			annotation = etree.SubElement(annotations, "Annotation")
			annotation.set("about", url)
			# We captured the number of times a link was mentioned, so could we potentially use that to refine the score?
			annotation.set("score", "1")
			label = etree.SubElement(annotation, "Label")
			label.set("name", cselabel)
		else:
			print '... and ignoring it...'
	return annotations

def getDomains(links,domainList={}):
	for url in links:
		netloc=urlparse(url)[1]
		if netloc.find('open.ac.uk')<0:
			if netloc in domainList:
				domainList[netloc]['count']=domainList[netloc]['count']+1
			else:
				domainList[netloc]={'domain':netloc,'cseInclude':'http://'+netloc+'/*','count':1}
	return domainList



######################## DO THE BUSINESS....
## Create an XML tree for the Annotations
cseAnnotations = etree.Element("Annotations")

## Grab a listing of the SA files in the target directory
listing = os.listdir(SA_XMLfiledir)

print 'Got listing'
## For each file, parse it as an XML doc, grab the links, and add them to the annotations list
##TO DO - this really needs tidying into a function
for page in listing:
	print page
	tree = etree.parse('/'.join([SA_XMLfiledir,page]))
	root = tree.getroot()
	links = root.findall(".//a[@href]")
	for link in links:
		externalLinks=addExternalLink(externalLinks,link)
	
cseAnnotations = addLinksToAnnotationsXML(cseAnnotations,externalLinks,cselabel)

#There may be occasions where we want to add the domains?
domainsList=getDomains(externalLinks)
print domainsList

xmlFileSave('tmp/testAnnotations.xml',cseAnnotations)

# Freemind Mindmap generator
## I want to get a feel for the structure around the links, and a mindmap visualisation might help with this
## In addition, the mimdmap view may be a useful spinoff...
mm=freemindRoot('t151Week10.xml')

xmlFileSave('tmp/test_full.mm',mm)
