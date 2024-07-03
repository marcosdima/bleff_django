from django.test import TestCase

from .models import Word, Language, Meaning

class WordModelTest(TestCase):
    def test_create_a_word(self):
        '''
            Create a word.
        '''
        text = 'House'
        word = Word.objects.create(word=text)
        self.assertIs(word.word, text)
        
