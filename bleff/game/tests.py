from django.forms import ValidationError
from django.test import TestCase

from .models import Word, Language, Meaning

class WordModelTest(TestCase):
    def test_create_a_word(self):
        '''
            Create a word.
        '''
        text = 'House'
        word = Word.objects.create(word=text)

        try:
            word.full_clean()
        except ValidationError:
            self.fail("Valid word raised ValidationError")

    
    def test_create_a_word_with_blank_as_value(self):
        '''
            Create a word with an empty string as word.
        '''
        word = Word(word='')
        with self.assertRaises(ValidationError):
            word.full_clean()


    def test_create_a_word_with_no_values(self):
        '''
            Create a word with no values passed.
        '''
        word = Word()
        with self.assertRaises(ValidationError):
            word.full_clean()
            

class LanguageModelTest(TestCase):
    def test_create_a_language(self):
        '''
            Create a new language.
        '''
        tag = 'EN'
        name = 'English'
        language = Language.objects.create(tag=tag, name=name)

        try:
            language.full_clean()
        except ValidationError:
            self.fail("Valid Language raised ValidationError")

    
    def test_create_a_language_with_blank_as_value(self):
        '''
            Create a new language with empty strings as values.
        '''
        language = Language(tag='', name='')
        with self.assertRaises(ValidationError):
            language.full_clean()


    def test_create_a_language_with_no_values(self):
        '''
            Create a word with no values passed.
        '''
        language = Language(tag='', name='')
        with self.assertRaises(ValidationError):
            language.full_clean()         
