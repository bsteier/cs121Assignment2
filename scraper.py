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

_visitedLinks = defaultdict(int)
data = ScraperManager.CurrentData()

def scraper(url, resp):
    checker = ScraperManager.ResponseValidity(resp)
    validity = checker.isValid()
    if type(validity) == str and is_valid(validity):
        return [validity]  # if it's a redirect, return the redirected website
    elif not validity:
        with open("fails.txt", "a") as fails:
            fails.write(str(url) + "\n")
            fails.write(str(resp.status) + "\n")
            fails.write(str(resp.error) + "\n")
            fails.write("\n")
        return list()
    
    
    curUrl = ScraperManager.Manager(url, resp)
    if data.compareHashSimilarity(curUrl.hashCode):
        return list()
    
    

    with open("unique.txt", "r") as u:
        count = int(u.read())
        count += 1
    with open("unique.txt", "w") as u:
        u.write(str(count))

    links = extract_next_links(url, resp)
    tba_links = [link for link in links if is_valid(link)]  #list of links to be added to the Frontier

    curUrl.save_data(len(tba_links), curUrl.get_total_word_count())
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
    if resp.status != 200: # this means we didn't get the page
        print("u suck")
        print(url)
        print(resp.error)
        print()

        return list()
    
    if not resp.raw_response:
        return list()   
    
    parsed = urlparse(url)

  #  print("URL", urlparse(url)== urlparse("https://www.ics.uci.edu"))
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")

    hyperlinks = soup.find_all("a", href=True) #finds all elements w/ an href

    words = soup.find_all(text=True)

    with open("websitecontents.txt", "w") as text: #write text content onto a file
        for w in words:
            text.write(w.text)

    linksToAdd = list()
    for link in set(hyperlinks):
        if urlparse(link['href']) == urlparse(url) or link['href'] in {"/"} or link['href'].startswith("mailto") or link['href'].startswith('#'): # avoid adding duplicates or invalid hrefs
            continue
        if not bool(urlparse(link['href']).netloc): #not absolute
            link2 = scraperHelper.convertToAbsolute(resp.url, link['href'])   # convert relative URLs to absolute
            if(link2 != parsed.geturl()):  # checks if the url we just created is the same as what we started with

                linksToAdd.append(link2)
                _visitedLinks[link2] += 1
        else:
            linksToAdd.append(link['href'])
            _visitedLinks[link['href']] += 1

    return list(set(linksToAdd))    #removes websites that are duplicates before sending to the frontier


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        #print(parsed.geturl())
        avoidUrls = {r"www.ics.uci.edu/~ziv/ooad/intro_to_se/", r"www.ics.uci.edu/Arcadia/Teamware/docs", r"swiki.ics.uci.edu/doku.php/projects:maint-spring-2018"} # websites that lead to a lot of links
        if any(u in url for u in avoidUrls):
            return False
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not re.search(r"\.ics\.uci\.edu/|\.cs\.uci\.edu/"
                     + r"|\.informatics\.uci\.edu/|\.stat\.uci\.edu/$", url):
            return False  # using regex to see if a url contains one of these domain patterns
        if parsed.fragment: 
            return False
        if url.lower().count("&do=media") and url.lower().count("doku.php") or url.lower().endswith("javascript:void(0)"): #re.match(r"(?=&do=media)(?=doku.php)", url.lower()):
            return False
        if url.count(".php") > 1 or url.count(r"www.ics.uci.edu/download") or url.count(r"~stasio/winter06/Lectures/"):
            return False
        if parsed.netloc == "wics.ics.uci.edu" and parsed.query.startswith("share"):
            return False
        return not re.match(
            r".*\.(r|css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|javascript:void(0))$|sql|apk|war|ma", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise


def getHash(resp, tokens) -> str:
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    words = soup.find_all(text=True)

    hashCode = simHash.generate_Fingerprint(tokens)
    return hashCode


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