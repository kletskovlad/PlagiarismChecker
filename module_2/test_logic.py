import unittest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_similarity(text1, text2):
    if not text1.strip() or not text2.strip():
        return 0

    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([text1, text2])
    return cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]


class TestPlagiarismLogic(unittest.TestCase):

    def test_identical(self):
        res = get_similarity("Тестовий рядок", "Тестовий рядок")
        self.assertTrue(res > 0.9)

    def test_different(self):
        res = get_similarity("Яблуко", "Машина")
        self.assertTrue(res < 0.5)

    def test_empty(self):
        res = get_similarity("", "Текст")
        self.assertEqual(res, 0)


if __name__ == "__main__":
    unittest.main()