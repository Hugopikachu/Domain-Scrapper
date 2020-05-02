# Domain Scrapper
A simple domain scrapper in Python.

## Working principle
Starts with a domain name and process every links on the initial page.

Add every link inside the domain to a queue of urls to be processed and move processed urls to a set of urls inside the domain.

Repeat the process until the queue of internal urls is consumed or the maximal number of iterations is reached.

### Inputs
A domain name in a 'domain-name.extension' pattern
	
### Outputs
a domain.txt file with every internal urls encountered

## How to use it
Simply clone the repository or download the domainScrapper.py file and run it from the directory you want to save your results.

### Usage
domainScrapper.py OPTIONS domain

### Options

	-h, --help            			show this help message and exit
  	-f, --save-files      			save html files into a subfolder of the current working directory
  	-s, --subdomains      			saves the encountered subdomains in a subdomains.txt file
  	-m MAX_ITER, --max-iter=MAX_ITER 	set the maximum number of urls explored
  	-v, --verbose         			print status messages to stdout


## Possible enhancements

* specify output destination instead of using current working directory
* build a sitemap.xml file instead of simply saving every urls encountered
* take into account other resources (.css, .js, .txt, .xml, images, ...) instead of only source code
* and many other 
	
Feel free to suggest modifications and reuse this code as you want ;)


