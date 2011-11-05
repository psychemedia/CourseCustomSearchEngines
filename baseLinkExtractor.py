# ESTEEM PROJECT (GOOGLE CUSTOM COURSE SEARCH ENGINES)
## Tony Hirst, a.j.hirst, Dept of Communication and Systems

## A minimal script to generate Google Custom Search Engine Annotations XML
## from links contained within OU VLE course webpages

## This is for initial testing purposes only

# DEPENDENCIES

## Quick hack approach - use lxml parser to parse SA XML files
from lxml import etree

#CONFIGURATION
## There's a little bit of config information we need

## The label of the custom search engine we want the annotations file to apply to
cselabel="_cse_*******"

## We can get copies of the XML versions of Structured Authoring documents
## that are rendered in the VLE by adding &content=1 to the end of the URL
## [via Colin Chambers]
## eg http://learn.open.ac.uk/mod/oucontent/view.php?id=526433&content=1

def simpleLinkExtractor(f,cselabel):
	# Create the root element of an XML doc for the CSE Annotations file
	annotations = etree.Element("Annotations")
	# Parse the passed in structured authoring (SA) file
	tree = etree.parse(f)
	# Find the root element of the parsed SA file
	root = tree.getroot()
	# Extract all the anchor elements
	links = root.findall(".//a[@href]")
	# Now run through all the anchor elements
	for link in links:
		# The href attribute is the linked to URL
		url = link.get('href')
		# Ser desc to the link text from each anchor element, just in case we need it
		desc = link.text
		# Create an annotation element for each link
		annotation = etree.SubElement(annotations, "Annotation")
		# Add the URL as an attribute to the annotation
		annotation.set("about", url)
		# Add a nominal CSE score to the annotation
		annotation.set("score", "1")
		# Create a label subelement on the annotation to identify the CSE it applies to
		label = etree.SubElement(annotation, "Label")
		# Set the ID of the required CSE
		label.set("name", cselabel)
	#Add a print statement for diagnostics
	print etree.tostring(annotations, pretty_print=True)
	return annotations

annotationsXML=simpleLinkExtractor('data/t151Week1.xml',cselabel)

