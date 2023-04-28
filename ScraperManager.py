from urllib.parse import urlparse
import os
import json
import tokenizer
from bs4 import BeautifulSoup
import simHash

STOPWORDS = ['a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 
             "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during', 'each', 'few', 'for', 
             'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's", 'her', 'here', 
             "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's", 'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', 
             "isn't", 'it', "it's", 'its', 'itself', "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 
             "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such', 'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 
             'themselves', 'then', 'there', "there's", 'these', 'they', "they'd", "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 
             'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 
             'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't", 'would', "wouldn't", 
             'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves']

class Manager:
    def __init__(self, url, resp):
        self.resp = resp
        self.parsed = urlparse(url)
        self.token_freq = self._get_tokens()
        self.hashCode = self._get_hash()

    def save_data(self, numOfLinks, wordCount):
       # if parsed_url.netloc == "www.ics.uci.edu":
        file_path = "saves.json"

        # Check if the file exists and initialize it with an empty JSON array if not
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                file.write("[]")

        # Iterate through the tba_links and append each URL data to the file
        url_data = {"url": self.resp.url, "hash": self.hashCode, "scraped": numOfLinks, "word count": wordCount}

        # Append the new URL data to the file
        with open(file_path, "rb+") as file:
            file.seek(-2, os.SEEK_END)  # Move the file pointer before the closing bracket
            file.truncate()  # Remove the closing bracket

            # Append the new URL data and add the closing bracket
            file.write(b",\n")  # Add a comma to separate the new entry
            file.write(json.dumps(url_data, indent=2).encode('utf-8'))
            file.write(b"\n]")

    def _get_tokens(self):
        soup = BeautifulSoup(self.resp.raw_response.content, "html.parser")
        words = soup.find_all(text=True)

        with open("websitecontents.txt", "w") as text: #write text content onto a file
            for w in words:
                if len(w) <= 1 or w in STOPWORDS:
                    continue
                else:
                    text.write(w.text)
        
        token_freq = tokenizer.computeWordFrequencies(tokenizer.tokenize("websitecontents.txt"))
        return token_freq

    def _get_hash(self):
        return simHash.generate_Fingerprint(self.token_freq)

    def get_total_word_count(self):
        """
        Returns the number of words found on a web page.
        """
        return sum(self.token_freq.values())

class CurrentData():
    problemHash = {'1100100110111000100110111011000011111001111000101101000000111010', '1000000100111010001110111010111101110001101110001000110000110000',
                    '1001110100110010010010001011111000100010100010000100001000000010',
                    '1000000110010011001110101011101101101000001000100010000000100000',
                    '1001000100110010011100111000111011100001111100001011010000110000',
                    '1101000100111110010010111110011011100001101110001010110000100000',
                    '1101000100011010010100111000011111100011111110101111111100110000'}  
    # {http://intranet.ics.uci.edu, https://www.ics.uci.edu/alumni/index.php, https://swiki.ics.uci.edu/doku.php/start?rev=1626126739&do=diff, https://swiki.ics.uci.edu/doku.php/virtual_environments:virtualbox?do=media&ns=virtual_environments, 
    # https://melissamazmanian.com/}

    visitedHash = set()

    def compareHashSimilarity(self, hashCode):
        """
        Returns true if hashCode is similar to one we have previosly seen.
        """
        #print("SIZE", len(self.visitedHashes))
        for h in self.visitedHash.union(self.problemHash):
            if simHash.calc_similarity(h, hashCode):
                return True

        if len(self.visitedHash) > 1200:  # when crawler starts to slow down
            self.visitedHash = set()
        self.visitedHash.add(hashCode)   
        return False


class ResponseValidity():
    """
    Based on the URL resp, checks if the page is valid by looking at status codes and size.
    """
    def __init__(self, resp):
        self.resp = resp  

    def isValid(self):
        """
        Performs all the validty checking and returns responses accordingly.
        Returns true if the response is valid.
        """
        if self._notFound():
            return False
        if self._isLarge():
            return False
        
        if type(self._isRedirect()) is str:
            return self._isRedirect()
        
        return True
    
    def _notFound(self) -> bool:
        """
        Checks a site's existence.
        """
        if not self.resp or not self.resp.raw_response:
            return True
        return self.resp.status == 404
    
    def _isLarge(self, max=599999):
        """
        Checks if a response is large.
        True: Contents won't be crawled.
        """
        return len(self.resp.raw_response.content) > max
    
    def _isRedirect(self):
        """
        Checks if a redirect is occuring.
        False: no redirect
        True/URL of redirected site.
        """

        if self.resp.raw_response.status_code in (301, 302): # check the status code of HTML obj to be safe
            return self.resp.raw_response.headers['Location']  # learned how to access redirection on ChatGPT
        return False

    def isLowQual(self, wordCount:int, min=100) -> bool:
        """
        Determines if a web response has low information based on its word count.
        True: low quality, don't scrape
        """
        return wordCount < min

    def canCrawl(self) -> bool:
        """
        Reads the sits robots.txt to see if we should crawl it.
        """
        return
    
    def parseSiteMap(self):
        """
        Returns a list of links to crawl based on sitemap.
        """
        return
    