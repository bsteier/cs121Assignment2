from urllib.parse import urlparse, urljoin

def convertToAbsolute(url, link):
    """
    Takes in a url and a scraped link.
    Converts the scraped link to an absolute link.
    """
    parsed = urlparse(url)
    if not link:
        return url
    if link.startswith("../"): # ../ tells us we want to access the parent of the url
        numBackDir = link.count("../")
        if not parsed.path or numBackDir >= len(parsed.path.split("/")) or numBackDir == len(parsed.path.split("/")) - 1:
            return urljoin(parsed.geturl(), link)
        else:
            updated_url = '/'.join(url.split('/')[:-1*(numBackDir)])
            link = link[numBackDir*3:]
            return updated_url + "/" + link
            
    return url + "/" + link