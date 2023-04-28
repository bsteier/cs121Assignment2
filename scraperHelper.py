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
    if not link:
        return url
    if not urlparse(link).scheme and urlparse("https://" + link).netloc:
        return urlparse("https://" + link).netloc
    
    if link.startswith("/") or link[0].isalnum() and link.count("/"): #not link.endswith((".html", ".htm", ".php")):  
        return urljoin(url, link)

    parsed = urlparse(url)
    if parsed.path and (parsed.path.endswith((".html", ".htm", ".php"))) or parsed.query:  
        parts = parsed.path.split("/")
        parts = "/".join(parts[:-1])
        url = urlunparse((parsed.scheme, parsed.netloc,
                          parts,
                          parsed.params,
                          "", ""))  # omit query and fragments
    
    parsedURL = urlparse(url + "/" + link)

    pathParts = parsedURL.path.split('/')
    updatedParts = list()

    for part in pathParts:
        if part == '..':  # ../ tells us that we want to access the parent of the current website domain
            if len(updatedParts) > 0:
                updatedParts.pop() # the end of a path shouldn't end in .. so there should be an obj in our list
        elif part:
            updatedParts.append(part)
    
    normalizedPath = "/".join(updatedParts)
    absoulteUrl = urlunparse((parsedURL.scheme, parsedURL.netloc, 
                              normalizedPath,
                              parsedURL.params,
                              parsedURL.query, '')) # omit fragments

    return absoulteUrl

