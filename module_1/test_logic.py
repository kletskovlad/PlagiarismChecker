import unittest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_similarity(text1, text2):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]

class TestPlagiarismLogic(unittest.TestCase):
    def test_identical(self):
        """Нормальні умови: однакові тексти"""
        self.assertAlmostEqual(get_similarity("Тест", "Тест"), 1.0)

    def test_different(self):
        """Граничні умови: різні тексти"""
        self.assertLess(get_similarity("Яблуко", "Машина"), 0.5)

if __name__ == "__main__":
    unittest.main()