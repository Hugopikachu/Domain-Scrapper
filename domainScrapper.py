#! /usr/bin/env python3

from requests import get
from bs4 import BeautifulSoup 
from os import path, makedirs
from optparse import OptionParser

def main() :
    parser = OptionParser(
        description="Explore a domain and saves every urls encountered in a txt file",
        usage="domainScrapper.py OPTIONS domain"
        )
    parser.set_defaults(save_files=False, subdomains=False, max_iter=2000, verbose=False)
    parser.add_option("-f", "--save-files", action="store_true", help="save html files into a subfolder of the current working directory", dest="save_files")
    parser.add_option("-s", "--subdomains", action="store_true", help="saves the encountered subdomains in a subdomains.txt file", dest="subdomains")
    parser.add_option("-m", "--max-iter", help="set the maximum number of urls explored", metavar="MAX_ITER", dest="max_iter", type="int")
    parser.add_option("-v", "--verbose", action="store_true", help="print status messages to stdout", dest="verbose")
    
    opts, args = parser.parse_args()

    if len(args) != 1 : 
        print(parser.print_help())
        exit(1)
    else :
        print("Exploring {}".format(args[0]))

        result = explore_domain(
            domain_name=args[0],
            save_files=opts.save_files,
            return_subdomains=opts.subdomains,
            max_iter=opts.max_iter,
            verbose=opts.verbose
        )

        with open("domain.txt", "w") as f:
            f.write("\n".join(result["domain"]))
        print("{} pages discovered ! Saved in domain.txt".format(len(result["domain"])))

        if opts.save_files : 
            print("html files saved to /pages subfolder")
            print("{} errors occured while saving html files".format(result["file_errors"]))

        if opts.subdomains :
            with open("subdomains.txt", "w") as f:
                f.write("\n".join(result["subdomains"]))
            print("{} subdomains discovered at {} ! Saved in subdomains.txt".format(len(result["subdomains"]), args[0]))

def get_domain(url):
    """
    Returns the domain of an url or an empty string if no domain found
    """
    try :
        return url.split("/")[2].strip("www.")
    except : return ""

def resolve_url(url, return_html=False):
    """
    Resolve an url and return its true url (after redirections).
    Returns the html code if asked
    """    
    page = get(url)
    if page.ok :
        if return_html: return page.url, page.text
        else : return page.url
    else :
        raise Exception(page.status_code)

def remove_query(url):
    """
    Naively removes query string from the url
    """
    return url.split("?")[0].split("#")[0]

def get_links(html):
    """
    Simply returns every href attributes of <a> tags in html by parsing with BeautifulSoup
    """
    soup = BeautifulSoup(html, 'html.parser')    
    return [tag.get("href", "") for tag in soup.find_all('a')]

def update_queue(new_urls, queue, explored_urls):
    """
    update the queue of remaining urls with the new urls that are not already explored
    """
    unexplored_urls = set(new_urls).difference(explored_urls)
    queue.update(unexplored_urls)

def filepath_from_url(url):
    """
    Returns the filepath following the url logic
    """
    url_split = [s for s in url.split("/") if s] # split at each /
    tree = url_split[2:] # extract the part of the url after the domain name
    
    # if there is nothing after the domain name, it is the root (index)
    if not tree : return "pages/index.html" 
    # else we create the path by recreating the hierarchy of the url
    # we remove the extension if it exists and add .html to the filename
    else : return ("pages/" + "/".join(tree)).rsplit(".", 1)[0] + ".html"

def save_html(html, file_path): 
    """
    Saves an html file at the location given by file_path
    """
    if not path.exists(path.dirname(file_path)) : # safeguard if the path doesn't exist
        makedirs(path.dirname(file_path)) 

    with open(file_path, "w", encoding='utf-8') as f:
        f.write(html)

def explore_domain(domain_name, save_files=False, return_subdomains=False, max_iter=2000, verbose=False):
    """
    Explore a domain iteratively by following intern links
    Saves the html files if asked
    Fix a maximum number of iterations as a safeguard to avoid overflows
    """
    
    domain = set() # the set of urls inside the domain
    subdomains = set() # to store subdomains encountered
    base_url = "https://www." + domain_name
    queue = set([base_url]) # the set of urls yet to explore - to be updated when new urls are encountered
    _iter=0
    _file_errors=0
        
    while queue :
        next_url = queue.pop()
        if verbose : print("Exploring {} ({} in queue)".format(next_url, len(queue)))
        
        try : url, html = resolve_url(next_url, True) # extract the first url and request the destination page
        except Exception as e :
            if verbose : print("   Error while requesting url ({})".format(e if type(e.args[0])==int else "Bad URL"))
            continue
            
        url = remove_query(url)    
        if url in domain : 
            if verbose : print ("   Already explored")
            continue
        
        found_urls = get_links(html) # get all urls in href attributes of <a> tags
        internal_urls = [url for url in found_urls if get_domain(url)==domain_name] # keep only urls inside the domain
        if return_subdomains : 
            subdomains_urls = [url for url in found_urls if (domain_name in get_domain(url)) and (domain_name != get_domain(url))] # keep links to subdomains only for informative purpose
        
        queue_size = len(queue) # to count the number of new urls
        update_queue(internal_urls, queue, domain)
        if verbose : print("   {} new pages discovered".format(len(queue) - queue_size))
        
        if save_files :
            try :
                file_path = filepath_from_url(url) # convert url to a file path
                save_html(html, file_path) # try and save the page to an html file
                if verbose : print("   Page saved at {}".format(file_path))
            except :
                _file_errors += 1
                if verbose : print("   Couldn't save the HTML file...")
  
        domain.update([url]) 
        if return_subdomains : subdomains.update([get_domain(url) for url in subdomains_urls])
        _iter += 1

        if _iter >= max_iter :
            print("Reached maximum number of iteration ({})".format(max_iter))
            break
            
    res = {"domain" : domain, "subdomains": None, "file_errors": None}
    if return_subdomains : res["subdomains"] = subdomains
    if save_files : res["file_errors"] = _file_errors

    return res

if (__name__ == "__main__") : main()
