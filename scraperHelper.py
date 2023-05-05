from urllib.parse import urlparse, urlunparse, urljoin
"""
    urlparse: breaks a url into parts
    urlunparse: constructs parts of a URL into a full URL
"""

def convertToAbsolute(url, link):
    """
    Takes in a url and a scraped link.
    Converts the scraped link to an absolute link.
    """
    # root-relative URL: means it's relative to the root/netloc of the current website
    # path-relative: means it's relative to the current directory of the base URL
    if not link:  # link doesn't exist so just return url
        return url
    if urlparse(link).scheme and urlparse(link).netloc:  # the link has a scheme and a netloc so it's valid
        return link
    if not urlparse(link).scheme and urlparse("https://" + link).netloc:  # the url doesn't have a scheme
        if urlparse("https://" + link).netloc == urlparse(url).netloc:   # with a scheme, the url's netloc is the same as the site scraped from
            return urlparse("https://" + link).netloc
    
    if link.startswith("/") or link[0].isalnum() and link.count("/"):  # if the link starts w/ a / or starts with a letter, then we construct the url 
        parsedURL = urlparse(urljoin(url, link))
        return urlunparse((parsedURL.scheme, parsedURL.netloc, 
                              parsedURL.path,
                              parsedURL.params,
                              parsedURL.query, '')) # omit fragments

    parsed = urlparse(url)
    if parsed.path and (parsed.path.endswith((".html", ".htm", ".php"))) or parsed.query:  # original url has endings that we want to omit when combining w/ the scraped link
        parts = parsed.path.split("/")
        parts = "/".join(parts[:-1])
        url = urlunparse((parsed.scheme, parsed.netloc,
                          parts,
                          parsed.params,
                          "", ""))  # omit query and fragments
    
    parsedURL = urlparse(url + "/" + link)  # combines the url and link

    pathParts = parsedURL.path.split('/')
    updatedParts = list()

    for part in pathParts:  # handles cases when there's a ..

        if part == '..':  # ../ tells us that we want to access the parent of the current website domain
            if len(updatedParts) > 0:
                updatedParts.pop() # the end of a path shouldn't end in .. so there should be something in our list
        elif part and part != ".":
            updatedParts.append(part)
    
    normalizedPath = "/".join(updatedParts)
    absoulteUrl = urlunparse((parsedURL.scheme, parsedURL.netloc, 
                              normalizedPath,
                              parsedURL.params,
                              parsedURL.query, '')) # omit fragments


    return absoulteUrl


def get_longest_page(url, token_freq:dict):
    """
    Writes the longest page scraped to longest.txt
    """
    total_words = sum(token_freq.values())
    with open("longest.txt", "r") as u:
        u.seek(0)
        if u.readline() == '':
            count = 0
        else:
            u.seek(0)
            count = int(u.readline())
        if total_words > count:
            with open("longest.txt", "w") as v:
                v.write(str(total_words) + "\n")
                v.write(url)


def get_unique_pages():
    """
    Writes to a file whenever a unique URL is found
    """
    try:
        with open("unique.txt", "r") as u:
            count = int(u.read())
            count += 1
        with open("unique.txt", "w") as u:
            u.write(str(count))
    except:
        with open("unique.txt", "w") as u:
            u.write(str(1))


def getICSSubDomains(url, numOfLinks):
    """
    Writes to a file the ICSSubDomains and the number of links scraped on that page
    """
    parsed = urlparse(url)
    if parsed.netloc.count("ics.uci.edu") and not parsed.path:
        with open("ICSSUBDomain.txt", "a") as ics:
            ics.write(str(url) + ", " + str(numOfLinks))
            ics.write("\n")