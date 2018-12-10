import logging
from datamodel.search.Yikangliu_datamodel import YikangliuLink, OneYikangliuUnProcessedLink
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter
from lxml import html,etree
import re, os
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs
from uuid import uuid4


max_url_count = 0
max_url = ""
subdomain_list = dict()
counter = 0


logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"

@Producer(YikangliuLink)
@GetterSetter(OneYikangliuUnProcessedLink)
class CrawlerFrame(IApplication):
    app_id = "Yikangliu"

    def __init__(self, frame):
        self.app_id = "Yikangliu"
        self.frame = frame


    def initialize(self):
        self.count = 0
        links = self.frame.get_new(OneYikangliuUnProcessedLink)
        if len(links) > 0:
            print "Resuming from the previous state."
            self.download_links(links)
        else:
            l = YikangliuLink("http://www.ics.uci.edu/")
            print l.full_url
            self.frame.add(l)

    def update(self):
        unprocessed_links = self.frame.get_new(OneYikangliuUnProcessedLink)
        if unprocessed_links:
            self.download_links(unprocessed_links)

    def download_links(self, unprocessed_links):
        for link in unprocessed_links:
            try:
                print "Got a link to download:", link.full_url
            except:
                print "Full url is not available"
            downloaded = link.download()
            links = extract_next_links(downloaded)
            for l in links:
                if is_valid(l):
                    self.frame.add(YikangliuLink(l))

    def shutdown(self):
        print (
            "Time time spent this session: ",
            time() - self.starttime, " seconds.")
        
        
def extract_next_links(rawDataObj):
    '''
    rawDataObj is an object of type UrlResponse declared at L20-30
    datamodel/search/server_datamodel.py
    the return of this function should be a list of urls in their absolute form
    Validation of link via is_valid function is done later (see line 42).
    It is not required to remove duplicates that have already been downloaded. 
    The frontier takes care of that.
    '''
    
    outputLinks = []

    import sys
    global subdomain_list
    global max_url_count
    global max_url
    global counter
    
    from lxml import html, etree
    from urlparse import urlparse, parse_qs, urljoin
    
    if rawDataObj.content:
        
        component =  urlparse(rawDataObj.url) 
        
        
        subdomain_list[component.netloc] = subdomain_list.get(component.netloc, 0) + 1 
        
        
        out_links = list()   
        
        links = html.fromstring(rawDataObj.content)  
        for item in links.iterlinks():    
            URL = item[2]                 
            
            if URL.startswith('http://') or URL.startswith('https://'): 
                outputLinks.append(URL)
                out_links.append(URL)
            
            elif URL.startswith('//'):   
                if not rawDataObj.is_redirected:    
                    URL_component = urlparse(rawDataObj.url)    
                    absolute_url = URL_component.scheme + "://" + URL_component.netloc + URL_component.path.rstrip('/')+ URL
                    outputLinks.append(absolute_url)
                    out_links.append(absolute_url)
  
                else:
                    URL_component = urlparse(rawDataObj.final_url)   
                    absolute_url = URL_component.scheme + "://" + URL_component.netloc + URL_component.path.rstrip('/')+ URL
                    outputLinks.append(absolute_url)
                    out_links.append(absolute_url)   
            
            else:
                if not rawDataObj.is_redirected:   
                    URL_component = urlparse(rawDataObj.url)    
                    base = URL_component.scheme + "://" + URL_component.netloc + URL_component.path
                    absolute_url = urljoin(base, URL)
                    outputLinks.append(absolute_url)
                    out_links.append(absolute_url)
                else:                              
                    URL_component = urlparse(rawDataObj.final_url)   
                    base = URL_component.scheme + "://" + URL_component.netloc + URL_component.path
                    absolute_url = urljoin(base, URL)
                    outputLinks.append(absolute_url)
                    out_links.append(absolute_url)
                          
        counter = counter + 1
                
        if(len(out_links) > max_url_count ):  
            max_url_count = len(out_links)
            max_url = rawDataObj.url
        try:    
            print("********************",counter, "***********************")
        except:
            pass
        
    if counter == 3000:   
        file = open('Analytics.txt', 'r+')
        file.write("URL with Maximum outgoing links : " + max_url + '    ' + "Maximum Links: " + str(max_url_count))
        file.write(' \n ')
        for key in subdomain_list:
            file.write('\n' + "Subdomain: " + key + '    ' + "Subdomain_count: " + str(subdomain_list[key]))
        print(" Reached maximum value")
        sys.exit(0)
            
    return outputLinks



used_links = set()

def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be
    downloaded or not.
    Robot rules and duplication rules are checked separately.
    This is a great place to filter out crawler traps.
    '''
    
    
    
    if not url:   
        return False
    
   
    
    global used_links    
    if url in used_links:
        return False
    used_links.add(url)
    
   
    parsed = urlparse(url)
    
    
   
    
    if not(parsed.scheme and parsed.netloc and parsed.path):  
        return False
    
   
    traps = ["calendar.ics.uci.edu", "archive.ics.uci.edu"]  
    for item in traps:
        if item in url:
            return False
        
   
    
    limit = 3
    if len(parse_qs(parsed.query)) >= limit:  
        return False
    
    
    
    rep = url.split('/')
    for item in rep:
        if rep.count(item) >= 2:
            return False
        
   
    
    long = url.split('/')
    if len(long) > 10:
        return False
    
    
    if parsed.scheme not in set(["http", "https"]):
        return False
    try:
        return ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        return False

