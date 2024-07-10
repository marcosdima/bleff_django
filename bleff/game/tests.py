from django.forms import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.contrib.auth.models import User

from .models import Word, Language, Meaning, Game, Play, Hand, Guess

def create_basic_meaning(word_translation: str, content: str):
    word = Word.objects.create(word='AnyWord')
    language = Language.objects.create(tag='En', name='English')

    return Meaning.objects.create(text=content, word_translation=word_translation, word=word, language=language)


def create_basic_user():
    return User.objects.create_user(username="root_test", password="password")


def create_basic_language():
    tag = 'EN'
    name = 'English'
    return Language.objects.create(tag=tag, name=name)


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
        word = Word.objects.create(word='')
        with self.assertRaises(ValidationError):
            word.full_clean()


    def test_create_a_word_with_no_values(self):
        '''
            Create a word with no values passed.
        '''
        word = Word.objects.create()
        with self.assertRaises(ValidationError):
            word.full_clean()
            

    def test_create_a_word_that_already_exists(self):
        '''
            Tries to duplicate a word.
        '''
        text = 'House'
        Word.objects.create(word=text)

        with self.assertRaises(IntegrityError):
            Word.objects.create(word=text)


    def test_word_str_function(self):
        text = 'House'
        word = Word.objects.create(word=text)
        self.assertEqual(text, word.__str__(), 'Str function does not works!')


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
        language = Language.objects.create(tag='', name='')
        with self.assertRaises(ValidationError):
            language.full_clean()


    def test_create_a_language_with_no_values(self):
        '''
            Create a word with no values passed.
        '''
        language = Language.objects.create(tag='', name='')
        with self.assertRaises(ValidationError):
            language.full_clean()         


    def test_create_a_language_with_invalid_tag(self):
        '''
            Create a new language with an invalid tag.
        '''
        tag = ''
        name = 'English'
        language = Language.objects.create(tag=tag, name=name)

        with self.assertRaises(ValidationError):
                    language.full_clean()         


    def test_create_a_language_with_invalid_name(self):
        '''
            Create a new language with an invalid name.
        '''
        tag = 'EN'
        name = 'EN'
        language = Language.objects.create(tag=tag, name=name)

        with self.assertRaises(ValidationError):
                    language.full_clean()


    def test_create_a_language_that_already_exists(self):
        '''
            Tries to duplicate a language.
        '''
        tag = 'EN'
        name = 'English'
        Language.objects.create(tag=tag, name=name)

        with self.assertRaises(IntegrityError):
            Language.objects.create(tag=tag, name=name)

    def test_language_str_function(self):
        tag = 'EN'
        name = 'English'
        language = Language.objects.create(tag=tag, name=name)
        self.assertEqual(f'{tag}-{name}', language.__str__(), 'Str function does not works!')


class MeaningModelTest(TestCase):
    def test_create_a_meaning(self):
        word = 'House'
        content = 'A place where you live.'
        meaning = create_basic_meaning(word_translation=word, content=content)

        try:
            meaning.full_clean() 
        except ValidationError:
            self.fail("Valid Meaning raised ValidationError")


    def test_create_a_meaning_with_word_translation_field_as_an_empty_string(self):
        '''
            Create a new meaning with empty strings as word_translation.
        '''
        word = ''
        content = 'A place where you live.'
        meaning = create_basic_meaning(word_translation=word, content=content)

        with self.assertRaises(ValidationError):
           meaning.full_clean()


    def test_create_a_meaning_with_content_field_as_an_empty_string(self):
        '''
            Create a new meaning with empty strings as content.
        '''
        word = 'House'
        content = ''
        meaning = create_basic_meaning(word_translation=word, content=content)

        with self.assertRaises(ValidationError):
           meaning.full_clean()


    def test_create_a_meaning_duplicated(self):
        word = Word.objects.create(word='House')
        lang = Language.objects.create(tag='En', name='English')
        content = 'A place where you live.'
        Meaning.objects.create(text=content, word_translation='House', word=word, language=lang)
        
        with self.assertRaises(IntegrityError):
           Meaning.objects.create(text=content, word_translation='House', word=word, language=lang)


    def test_meaning_str_function(self):
        word = 'House'
        content = 'A place where you live.'
        meaning = create_basic_meaning(word_translation=word, content=content)
        self.assertEqual(f'{word}: {content}', meaning.__str__(), 'Str function does not works!')


class GameModelTest(TestCase):
    def setUp(self):
        self.user = create_basic_user()
        self.lang = create_basic_language()


    def test_create_a_game(self):
        '''
            Tries to create a game.
        '''
        game = Game.objects.create(idiom=self.lang, creator=self.user)

        try:
            game.full_clean()
        except ValidationError:
            self.fail("Valid Game raised ValidationError")


    def test_create_a_game_with_creator_as_none(self):
        '''
            Tries to create a game with creator as none.
        '''
        game = Game.objects.create(idiom=self.lang, creator=None)

        try:
            game.full_clean()
        except ValidationError:
            self.fail("Valid Meaning raised ValidationError")


    def test_create_a_game_with_no_language(self):
        '''
            Tries to create a game with language as none.
        '''        
        with self.assertRaises(IntegrityError):
           Game.objects.create(idiom=None, creator=self.user)


    def test_game_str_function(self):
        game = Game.objects.create(idiom=self.lang, creator=self.user)
        self.assertEqual(f'Game {game.id}: created by {self.user.username}', game.__str__(), 'Str function does not works!')


    def test_game_str_function_with_none_as_creator(self):
        game = Game.objects.create(idiom=self.lang, creator=None)
        self.assertEqual(f'Game {game.id}: created by SECRET', game.__str__(), 'Str function does not works!')


class PlayModelTest(TestCase):
    def setUp(self):
        self.user = create_basic_user()
        self.secondaryUser = User.objects.create_user(username='second', password='1234')
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)


    def test_create_a_play_instance(self):
        '''
            Creates a play instance of secondary player and self.game.
        '''
        play = Play.objects.create(game=self.game, user=self.secondaryUser)

        try:
            play.full_clean()
        except ValidationError:
            self.fail("Valid Play raised ValidationError")


    def test_create_a_play_of_a_player_that_already_plays(self):
        '''
            Tries to create a duplicated play instance.
        '''
        Play.objects.create(game=self.game, user=self.secondaryUser)
        with self.assertRaises(IntegrityError):
           Play.objects.create(game=self.game, user=self.secondaryUser)


    def test_create_a_play_of_a_player_that_already_plays_beacuse_they_created_the_game(self):
        '''
            Tries to create a play instance of self.user and self.game, but self.user created the game so their instance of 'play' should already be created,
            triggering an IntegrityError.
        '''
        with self.assertRaises(IntegrityError):
           Play.objects.create(game=self.game, user=self.user)


class HandModelTest(TestCase):
    def setUp(self):
        self.user = create_basic_user()
        self.secondaryUser = User.objects.create_user(username='second', password='1234')
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)
        self.word = Word.objects.create(word='House')
        self.meaning = Meaning.objects.create(text='An explanation of what it is in English.', language=self.lang, word=self.word, word_translation='HoUsE')


    def test_create_a_new_hand(self):
        '''
            Create a new hand with valid data.
        '''
        try:
            h = Hand.objects.create(game=self.game, leader=self.user, word=self.word)
        except ValidationError or IntegrityError:
            self.fail("Valid Hand raised an error")


    def test_create_a_new_hand_with_no_leader(self):
        '''
            Create a new hand without valid data (missing leader).
        '''
        with self.assertRaises(IntegrityError):
            hand = Hand.objects.create(game=self.game, word=self.word)
            hand.full_clean()

    
    def test_create_a_new_hand_with_no_game(self):
        '''
            Create a new hand without valid data (missing game).
        '''
        with self.assertRaises(IntegrityError):
            hand = Hand.objects.create(leader=self.user, word=self.word)
            hand.full_clean()


    def test_create_a_new_hand_with_no_word(self):
        '''
            Create a new hand without valid data (missing word).
        '''
        with self.assertRaises(IntegrityError):
            hand = Hand.objects.create(leader=self.user, game=self.game)
            hand.full_clean()


    def test_create_a_new_hand_with_a_word_without_meaning(self):
        '''
            Create a new hand with a word with no meaning in the Game idiom.
        '''
        with self.assertRaises(ValidationError):
            Hand.objects.create(leader=self.user, game=self.game, word=Word.objects.create(word='AnyWord'))


    def test_create_a_new_hand_with_an_outsider_as_leader(self):
        '''
            Create a new hand with a leader that does not belong to Game.
        '''
        with self.assertRaises(ValidationError):
            Hand.objects.create(game=self.game, leader=self.secondaryUser)


class GuessModelTest(TestCase):
    def setUp(self):
        self.user = create_basic_user()
        self.secondaryUser = User.objects.create_user(username='second', password='1234')
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)
        self.word = Word.objects.create(word='House')
        self.meaning = Meaning.objects.create(text='An explanation of what it is in English.', language=self.lang, word=self.word, word_translation='HoUsE')
        self.hand = Hand.objects.create(game=self.game, leader=self.user, word=self.word)
        self.content = 'A guess of a Hand, LOL.'


    def test_create_a_guess(self):
        '''
            Create a valid Guess.
        '''
        try:
            Guess.objects.create(hand=self.hand, content=self.content, writer=self.user)
        except ValidationError or IntegrityError:
            self.fail('A Valid Guess creation raised an error')

    
    def test_create_a_guess_with_no_hand(self):
        '''
            Raises an error because Guess has no hand.
        '''
        with self.assertRaises(IntegrityError):
            Guess.objects.create(content=self.content, writer=self.user)


    def test_create_a_guess_with_no_content(self):
        '''
            Raises an error because Guess has no content.
        '''
        with self.assertRaises(ValidationError):
            g = Guess.objects.create(hand=self.hand, writer=self.user)
            g.full_clean()


    def test_create_a_guess_with_no_writer(self):
        '''
            Raises an error because Guess has no writer.
        '''
        with self.assertRaises(ValidationError):
            Guess.objects.create(hand=self.hand, content=self.content)


    def test_create_a_guess_after_create_hand(self):
        '''
            When a Hand is created, a Guess with the right content has to be created too.
        '''
        # In 'setUp' self.hand was created.
        right = Guess.objects.filter(hand=self.hand)[0]
        self.assertEqual(True, right != None)
        self.assertEqual(True, right.is_original)


    def test_create_a_guess_with_is_original_as_true(self):
        '''
            The only guess that can be the 'original', is the one created by default after a Hand is created.
        '''
        with self.assertRaises(ValidationError):
            Guess.objects.create(hand=self.hand, content=self.content, writer=self.user, is_original=True)


    
    def test_a_guess_writer_can_be_none_just_in_is_the_original_case(self):
        '''
            The only Guess that accepts writer as None is the first one, the right one.
        '''
        with self.assertRaises(ValidationError):
            Guess.objects.create(hand=self.hand, content=self.content, writer=None)
