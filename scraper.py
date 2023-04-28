import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from collections import defaultdict
import simHash
import tokenizer
import json
import scraperHelper

_visitedLinks = defaultdict(int)

def scraper(url, resp):
    if resp.status == 200:
        if len(resp.raw_response.content) > 5000000:  #don't scrape a website that's too large
            return list()
    
    links = extract_next_links(url, resp)
    tba_links = [link for link in links if is_valid(link)]  #list of links to be added to the Frontier

    if urlparse(url) == urlparse("https://www.stat.uci.edu"):
        with open("icsSubDomain.json", "a") as ics:
            for link in tba_links:
                ics.write(json.dumps({"url": link}) + "\n") # ics.write(link)
                ics.flush() # ics.write("\n")
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

        with open("fails.txt", "a") as fails:
            fails.write(str(url) + "\n")
            fails.write(str(resp.status) + "\n")
            fails.write(str(resp.error) + "\n")
            fails.write("\n")

        return list()
    
    # CHECK SIMILARITY against problem sites
    hashCode = getHash(resp)
    problemSites = {'1100100110111000100110111011000011111001111000101101000000111010', '1000000100111010001110111010111101110001101110001000110000110000'
                    , '1000010100101000010010011001111001100001101110101110101001110000'}  # {http://intranet.ics.uci.edu, https://www.ics.uci.edu/alumni/index.php, http://www.ics.uci.edu/ugrad/courses/listing.php?year=2016&level=Lower-Division&department=STATS&program=ALL//ugrad/policies/Add_Drop_ChangeOption}
    for h in problemSites:
        if simHash.calc_similarity(hashCode, h):
            return list()
    with open("downloaded.txt", "a") as downloaded:
        downloaded.write(url + '\n')
        downloaded.write("\t" + hashCode + "\n")
        downloaded.write("\tsize " + str(len(resp.raw_response.content)) + "\n")
        
    
    parsed = urlparse(url)

  #  print("URL", urlparse(url)== urlparse("https://www.ics.uci.edu"))
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")

    hyperlinks = soup.find_all("a", href=True) #finds all elements w/ an href

    words = soup.find_all(text=True)

    with open("websitecontents.txt", "w") as text: #write text content onto a file
        for w in words:
            text.write(w.text)
                
    
        #for w in words:
         #   downloaded.write(w.text.strip())
           
        

    linksToAdd = list()
    for link in hyperlinks:
        if urlparse(link['href']) == urlparse(url) or link['href'] in {"/"} or link['href'].startswith("mailto") or link['href'].startswith('#'): # avoid adding duplicates or invalid hrefs
            continue
        if not bool(urlparse(link['href']).netloc): #not absolute
            link2 = scraperHelper.convertToAbsolute(resp.url, link['href'])   # convert relative URLs to absolute
            if(link2 != parsed.geturl()):  # checks if the url we just created is the same as what we started with
                with open("fails2.txt", "a") as fails:
                    fails.write("CURRENT: " + str(url) + "\n")
                    fails.write(link['href'] + '\n')
                    fails.write(link2 + '\n')
                    fails.write("\n")

                linksToAdd.append(link2)
                _visitedLinks[link2] += 1
        else:
            linksToAdd.append(link['href'])
            _visitedLinks[link['href']] += 1
    
   # print("URL", urlparse(url).netloc == urlparse("https://www.ics.uci.edu").netloc)
        #print("RESPONSE", resp.raw_response.content)

    return list(set(linksToAdd))    #!need a way to remove websites that have already been scraped


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not re.search(r"\.ics\.uci\.edu/|\.cs\.uci\.edu/"
                     + r"|\.informatics\.uci\.edu/|\.stat\.uci\.edu/$", url):
            return False  # using regex to see if a url contains one of these domain patterns
        return not re.match(
            r".*\.(r|css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise


def getHash(resp) -> str:
    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    words = soup.find_all(text=True)

    with open("websitecontents.txt", "w") as text: #write text content onto a file
        for w in words:
            text.write(w.text)
    hashCode = simHash.generate_Fingerprint(tokenizer.computeWordFrequencies(tokenizer.tokenize("websitecontents.txt")))
    return hashCode

