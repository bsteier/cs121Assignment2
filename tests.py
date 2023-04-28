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

    def test1(self):
        f1 = "1000010100101000010010011001111001100001101110101110101001110000"  # http://www.ics.uci.edu/ugrad/courses/listing.php?year=2016&level=Lower-Division&department=STATS&program=ALL//ugrad/policies/Add_Drop_ChangeOption
        f2 = "1001000100111000111010011001111001100001110110101110001000110000"  # http://www.ics.uci.edu/ugrad/courses/listing.php?year=2016&level=Lower-Division&department=STATS&program=ALL
        self.assertFalse(simHash.calc_similarity(f1, f2))
    

class TestRelativeToAbsolute(unittest.TestCase):
    def test10(self):
        url = r'https://www.ics.uci.edu/grad/policies'
        scraped = r'../../about/visit/index.php'

        expected_link = r'https://www.ics.uci.edu/about/visit/index.php'
        self.assertEqual(scraperHelper.convertToAbsolute(url, scraped), expected_link)
    
    def test20(self):
        url = r'https://www.ics.uci.edu/grad/policies'
        scraped = r'../resources.php'

        expected_link = r'https://www.ics.uci.edu/grad/resources.php'
        self.assertEqual(scraperHelper.convertToAbsolute(url, scraped), expected_link)

    def test30(self):
        url = r'https://www.ics.uci.edu/grad/policies'
        scraped = r'../../../computing/account/new.php'

        expected_link = r'https://www.ics.uci.edu/computing/account/new.php'
        self.assertEqual(scraperHelper.convertToAbsolute(url, scraped), expected_link)

    def test40(self):
        url = r'https://www.ics.uci.edu/employment'
        scraped = r'employ_faculty.php'

        expected_link = r'https://www.ics.uci.edu/employment/employ_faculty.php'
        self.assertEqual(scraperHelper.convertToAbsolute(url, scraped), expected_link)

    def test50(self):
        url = r"https://www.ics.uci.edu/community/news/view_news.php?id=2222"
        scraped = r"../../about/annualreport/index.php"

        expected_link = r"https://www.ics.uci.edu/about/annualreport/index.php"
        self.assertEqual(scraperHelper.convertToAbsolute(url, scraped), expected_link)

    def test60(self):
        url = r"http://www.ics.uci.edu/community/news/articles/view_article?id=66"
        scraped = r"../index.php"

        expected_link = r"http://www.ics.uci.edu/community/news/index.php"
        self.assertEqual(scraperHelper.convertToAbsolute(url, scraped), expected_link)

    def test70(self):
        url = r"http://www.ics.uci.edu/grad/Course_updates"
        scraped = r"funding/housing.php"
        expected_link = r"http://www.ics.uci.edu/grad/funding/housing.php"

        self.assertEqual(scraperHelper.convertToAbsolute(url, scraped), expected_link)

    def test80(self):
        url = r"http://www.ics.uci.edu/~emilyo/SimSE"
        scraped = r"details.html"
        expected_link = r"http://www.ics.uci.edu/~emilyo/SimSE/details.html"

        self.assertEqual(scraperHelper.convertToAbsolute(url, scraped), expected_link)



if __name__ == "__main__":
    unittest.main()