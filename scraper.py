import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from collections import defaultdict
import simHash
import tokenizer
import json
import scraperHelper
import os
import ScraperManager


data = ScraperManager.CurrentData()

def scraper(url, resp):
    checker = ScraperManager.ResponseValidity(resp)
    validity = checker.isValid()
    if type(validity) == str and is_valid(validity):
        return [validity]  # if it's a redirect, return the redirected website
    elif not validity:
        return list()

    curUrl = ScraperManager.Manager(url, resp)
    scraperHelper.get_longest_page(url, curUrl.token_freq)
    scraperHelper.get_unique_pages()
    
    # compare hash similarities
    if data.compareHashSimilarity(curUrl.hashCode):
        with open("fails.txt", "a") as fails:
            fails.write("SIMILAR " + str(resp.url) + "\n")

        return list()
    
    
    links = extract_next_links(url, resp)
                
    tba_links = [link for link in links if is_valid(link)]  #list of links to be added to the Frontier
    scraperHelper.getICSSubDomains(url, len(tba_links))

    # check if the site is low quality 
    if checker.isLowQual(curUrl.get_total_word_count(), len(tba_links)):
        return list()
    
    curUrl.save_data(len(tba_links), curUrl.get_total_word_count())  # save the data of sites that are valid
    return tba_links

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    if resp.status != 200 or not resp.raw_response: # EXTRA CHECK: this means we didn't get the page
        return list()
    

    parsed = urlparse(url)

    try:
        soup = BeautifulSoup(resp.raw_response.content, "html.parser")
        hyperlinks = soup.find_all("a", href=True)  # finds all elements w/ an href
    except RecursionError:    # our beautiful soup object is not in html/cannot be read
        with open("fails.txt", "a") as fails:
            fails.write(str(url) + "\n")
            fails.write(str(resp.status) + "\n")
            fails.write(str(resp.error) + "\n")
            fails.write("\n")
        return list()

    # composing our list of potential URLs
    linksToAdd = list()
    for link in set(hyperlinks):
        if urlparse(link['href']) == urlparse(url) or link['href'] in {"/"} or link['href'].startswith("mailto") or link['href'].startswith('#'): # avoid adding duplicates or invalid hrefs
            continue
        else:  # convert
            link2 = scraperHelper.convertToAbsolute(resp.url, link['href'])   # convert relative URLs to absolute
            if(link2 != parsed.geturl()):  # checks if the url we just created is the same as what we started with
                linksToAdd.append(link2)



    return list(set(linksToAdd))    #removes websites that are duplicates before sending to the frontier


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.d
    try:
        parsed = urlparse(url)

        
        avoidUrls = {r"http://alumni.ics.uci.edu", r"http://fano.ics.uci.edu/", r"http://checkmate.ics.uci.edu", r"www.ics.uci.edu/ugrad/courses/listing.php", r"www.ics.uci.edu/~ziv/ooad/intro_to_se/",
        }
                #r"swiki.ics.uci.edu/doku.php/projects:maint-spring-2018"} # websites that lead to a lot of links
        # r"www.ics.uci.edu/Arcadia/Teamware/docs"
        if any(u in url for u in avoidUrls):
            return False
        if parsed.path: # check for repeated paths
            p = [p for p in parsed.path.split("/") if p]

            visited = set()
            for token in p:
                if token not in visited:
                    if p.count(token) > 2:  #if a path part is repeated more tokens
                        return False
                    else:
                        visited.add(token) 
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not any(a in url for a in (".ics.uci.edu/", ".cs.uci.edu/", ".informatics.uci.edu/", ".stat.uci.edu/" )):
            return False
        if len(parsed.query) > 50:  #long queries = bad 
            return False
        if parsed.fragment or any(url.lower().count(a) for a in ("javascript:", "mailto:", ".bam", ".ff", ".war", ".lif")): # bad endings
            return False
      #  if url.lower().count("&do=media") and url.lower().count("doku.php"):
         #   return False
        if url.count(r"www.ics.uci.edu/download") or url.count(r"~stasio/winter06/Lectures/"): # links that are low content  (ics: attempts to download, stasio: links to ppts)
            return False
        if parsed.netloc == "wics.ics.uci.edu" and parsed.query.startswith("share"):  # in wics, there are many different ways to share a page but each query with share leads to the same page
            return False
     #   if url.lower().count("https://archive.ics.uci.edu/ml/datasets.php") and parsed.query: #  queries take u to the same page for this site
      #      return False
        return not re.match(
            r".*\.(r|css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|javascript:void(0)|sql|apk|war|ma)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise




"""
                with open("fails2.txt", "a") as fails:
                    fails.write("CURRENT: " + str(url) + "\n")
                    fails.write(link['href'] + '\n')
                    fails.write(link2 + '\n')
                    fails.write("\n")

    # CHECK SIMILARITY against problem sites
    hashCode = getHash(resp, token_freq)
    problemSites = {'1100100110111000100110111011000011111001111000101101000000111010', '1000000100111010001110111010111101110001101110001000110000110000',
                    '1001110100110010010010001011111000100010100010000100001000000010',
                    '1000000110010011001110101011101101101000001000100010000000100000',
                    '1001000100110010011100111000111011100001111100001011010000110000',
                    '1101000100111110010010111110011011100001101110001010110000100000'}  
    # {http://intranet.ics.uci.edu, https://www.ics.uci.edu/alumni/index.php, https://swiki.ics.uci.edu/doku.php/start?rev=1626126739&do=diff, https://swiki.ics.uci.edu/doku.php/virtual_environments:virtualbox?do=media&ns=virtual_environments, 
    # https://melissamazmanian.com/}
    for h in problemSites:
        if simHash.calc_similarity(hashCode, h):
            return list()
    scraperHelper.get_longest_page(resp.url, token_freq)    

    with open("downloaded.txt", "a") as downloaded:
        downloaded.write(url + '\n')
        downloaded.write("\t" + hashCode + "\n")
        downloaded.write("\tsize " + str(len(resp.raw_response.content)) + "\n")

    if urlparse(url) == urlparse("https://www.stat.uci.edu"):
        with open("icsSubDomain.json", "a") as ics:
            for link in tba_links:
                ics.write(json.dumps({"url": link}) + "\n") # ics.write(link)
                ics.flush() # ics.write("\n")
"""