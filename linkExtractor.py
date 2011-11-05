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

# DEPENDENCIES
## We're going to load files in from a course related directory
import os
## Quick hack approach - use lxml parser to parse SA XML files
from lxml import etree
## When we test URLs, we might as well be able to parse them comprehensively
from urlparse import urlparse

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

## Create an XML tree for the Annotations
cseAnnotations = etree.Element("Annotations")

## Grab a listing of the SA files in the target directory
listing = os.listdir(SA_XMLfiledir)

print 'Got listing'
## For each file, parse it as an XML doc, grab the links, and add them to the annotations list
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

# Output
fon='test.xml'
str = etree.tostring(cseAnnotations, pretty_print=True)
print str
fout=open(fon,'wb+')
fout.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
fout.write(str)
fout.close()