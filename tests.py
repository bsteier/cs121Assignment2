import unittest
import tokenizer
import simHash
import scraperHelper

from pathlib import Path

class TestSimilarity(unittest.TestCase):
    def test_simpleFiles(self):
        p1 = Path(r"TestFiles/a.txt")
        p2 = Path(r"TestFiles/b.txt")

        freq1 = tokenizer.computeWordFrequencies(tokenizer.tokenize(p1))
        freq2 = tokenizer.computeWordFrequencies(tokenizer.tokenize(p2))

        f1 = simHash.generate_Fingerprint(freq1)
        f2 = simHash.generate_Fingerprint(freq2)

        self.assertTrue(simHash.calc_similarity(f1, f1))

    def test_twoWebsites(self):
        f1 = '1100100110111000100110111011000011111001111000101101000000111010'  # http://intranet.ics.uci.edu
        f2 = '1100100111111000100110101011010011101001111000101101000000111010'  # http://intranet.ics.uci.edu/doku.php/start?do=login&sectok=
        self.assertTrue(simHash.calc_similarity(f1, f2))
        
    def test_twoDissimilarSites(self):
        f1 = '1100100110111000100110111011000011111001111000101101000000111010'  # http://intranet.ics.uci.edu
        f2 = '1001000100111000111010011001111001100001110110101110001000110000'  # http://www.ics.uci.edu/ugrad/courses/listing.php?year=2016&level=Lower-Division&department=STATS&program=ALL
        self.assertFalse(simHash.calc_similarity(f1, f2))

    def test_twoDissimilarSites2(self):
        f1 = '1001000100110000001110111000111001100011011110011010011101111100'  # https://www.stat.uci.edu
        f2 = '1011000100111110001110111001111101100001011110001011010001110000'  # https://statconsulting.ics.uci.edu
        self.assertFalse(simHash.calc_similarity(f1, f2))

class TestRelativeToAbsolute(unittest.TestCase):
    def test1(self):
        url = r'https://www.ics.uci.edu/grad/policies'
        scraped = r'../../about/visit/index.php'

        expected_link = r'https://www.ics.uci.edu/about/visit/index.php'
        self.assertEqual(scraperHelper.convertToAbsolute(url, scraped), expected_link)
    
    def test2(self):
        url = r'https://www.ics.uci.edu/grad/policies'
        scraped = r'../resources.php'

        expected_link = r'https://www.ics.uci.edu/grad/resources.php'
        self.assertEqual(scraperHelper.convertToAbsolute(url, scraped), expected_link)

    def test3(self):
        url = r'https://www.ics.uci.edu/grad/policies'
        scraped = r'../../../computing/account/new.php'

        expected_link = r'https://www.ics.uci.edu/computing/account/new.php'
        self.assertEqual(scraperHelper.convertToAbsolute(url, scraped), expected_link)

    def test4(self):
        url = r'https://www.ics.uci.edu/employment'
        scraped = r'employ_faculty.php'

        expected_link = r'https://www.ics.uci.edu/employment/employ_faculty.php'
        self.assertEqual(scraperHelper.convertToAbsolute(url, scraped), expected_link)


if __name__ == "__main__":
    unittest.main()