from datetime import timedelta
from django.utils import timezone
from django.forms import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.contrib.auth.models import User

from .models import Word, Language, Meaning, Game, Play, Hand, Guess, HandGuess, Vote

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
        self.word_2 = Word.objects.create(word='DOU')
        self.meaning = Meaning.objects.create(text='An explanation of what it is in English.', language=self.lang, word=self.word, word_translation='HoUsE')
        self.meaning_2 = Meaning.objects.create(text='An explanation of what it is in English.', language=self.lang, word=self.word_2, word_translation='DO')


    def test_create_a_new_hand(self):
        '''
            Create a new hand with valid data.
        '''
        try:
            Hand.objects.create(game=self.game, leader=self.user, word=self.word)
        except ValidationError or IntegrityError:
            self.fail("Valid Hand raised an error")


    def test_create_a_new_hand_with_no_leader(self):
        '''
            Create a new hand without 'leader'. The leader should be setted by default as the game creator (Beacuase is the only player)
        '''
        hand = Hand.objects.create(game=self.game, word=self.word)
        self.assertIsNot(None, hand.leader)
        self.assertEqual(self.game.creator.id, hand.leader.id)

    
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


    def test_finish_hand(self):
        '''
            Sets finished_at as now.
        '''
        finished = timezone.now() + timedelta(days=1)
        hand = Hand.objects.create(game=self.game, leader=self.user, word=self.word)
        hand.finished_at = finished
        hand.save()
        self.assertEqual(finished, Hand.objects.filter(id=hand.id)[0].finished_at)


    def test_finish_hand_before_started(self):
        '''
            Tries to set a finishing time that happend before the starting time.
        '''
        with self.assertRaises(ValidationError):
            hand = Hand.objects.create(game=self.game, leader=self.user, word=self.word)
            hand.finished_at = timezone.now() - timedelta(days=1)
            hand.save()


    def  test_hand_word_realtion_is_unique(self):
        '''
            In a game can not appear the same word twice.
        '''
        first = Hand.objects.create(game=self.game, leader=self.user, word=self.word)
        first.finished_at = timezone.now()
        first.save()
        with self.assertRaises(IntegrityError):
            Hand.objects.create(game=self.game, leader=self.user, word=self.word)


    def test_hand_can_not_be_created_if_there_is_another_unfinished(self):
        '''
            A hand can't be created if exists another with finished_at as None.
        '''
        Hand.objects.create(game=self.game, leader=self.user, word=self.word)
        
        with self.assertRaises(ValidationError):
            Hand.objects.create(game=self.game, leader=self.user, word=self.word_2)


    def test_hand_leader_default_setter_rotates_players(self):
        '''
            A hand can't be created if exists another with finished_at as None.
        '''
        Play.objects.create(game=self.game, user=self.secondaryUser)

        first = Hand.objects.create(game=self.game, leader=self.user, word=self.word)
        first.finished_at = timezone.now()
        first.save()
        
        second = Hand.objects.create(game=self.game, word=self.word_2)
        self.assertEqual(second.leader.id, self.secondaryUser.id)


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


class HandGuessModelTest(TestCase):
    def setUp(self):
        self.user = create_basic_user()
        self.secondaryUser = User.objects.create_user(username='second', password='1234')
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)
        self.word = Word.objects.create(word='House')
        self.meaning = Meaning.objects.create(text='An explanation of what it is in English.', language=self.lang, word=self.word, word_translation='HoUsE')
        self.hand = Hand.objects.create(game=self.game, leader=self.user, word=self.word)
        self.content = 'A guess of a Hand, LOL.'


    def test_after_guess_is_created_a_handguess_is_created_too(self):
        '''
            Checks if after a Guess is created, a HandGuess is created too.
        '''
        guess = Guess.objects.create(hand=self.hand, content=self.content, writer=self.user)
        self.assertEqual(1, HandGuess.objects.filter(hand=self.hand, guess=guess).count())
        self.assertEqual(2, len(HandGuess.objects.all()))


    def test_cant_exists_handguess_duplicates(self):
        '''
            Tries to create a HandGuess by hand.
        '''
        guess = Guess.objects.create(hand=self.hand, content=self.content, writer=self.user)
        with self.assertRaises(IntegrityError):
            HandGuess.objects.create(hand=self.hand, guess=guess)


    def test_is_correct_should_be_false_by_default(self):
        '''
            Check if is_correct field has the value False by default.
        '''
        guess = Guess.objects.create(hand=self.hand, content=self.content, writer=self.user)
        self.assertEqual(False, HandGuess.objects.get(hand=self.hand, guess=guess).is_correct)


    def test_is_correct_can_be_changed(self):
        guess = Guess.objects.create(hand=self.hand, writer=self.user)
        handguess = HandGuess.objects.get(hand=self.hand, guess=guess)
        self.assertEqual(False, handguess.is_correct)
        
        handguess.is_correct = True
        handguess.save()

        handguess_post_save = HandGuess.objects.get(hand=self.hand, guess=guess)
        self.assertEqual(True, handguess_post_save.is_correct)


    def test_is_correct_can_be_changed_unless_it_is_the_default_guess(self):
        '''
            Check if the default guess HandGuess has 'is_correct' field as False by default.
        '''
        guess = Guess.objects.get(hand=self.hand, writer=None)
        hand_guess = HandGuess.objects.get(hand=self.hand, guess=guess)
        with self.assertRaises(ValidationError):
            hand_guess.is_correct = True
            hand_guess.save()

    
    def test_is_correct_can_be_changed_but_just_one_time(self):
        guess = Guess.objects.create(hand=self.hand, writer=self.user)
        handguess = HandGuess.objects.get(hand=self.hand, guess=guess)
        handguess.is_correct = True
        handguess.save()

        with self.assertRaises(ValidationError):
            handguess.is_correct = False
            handguess.save()


class VoteModelTest(TestCase):
    def setUp(self):
        self.user = create_basic_user()
        self.secondaryUser = User.objects.create_user(username='second', password='1234')
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)
        self.word = Word.objects.create(word='House')
        self.meaning = Meaning.objects.create(text='An explanation of what it is in English.', language=self.lang, word=self.word, word_translation='HoUsE')
        self.hand = Hand.objects.create(game=self.game, leader=self.user, word=self.word)
        self.content = 'A guess of a Hand, LOL.'
        self.guess = Guess.objects.create(hand=self.hand, content=self.content, writer=self.user)
        self.secondary_guess = Guess.objects.create(hand=self.hand, content=self.content, writer=self.secondaryUser)
    

    def test_vote(self):
        '''
            Emulate a valid vote.
        '''
        try:
            Vote.objects.create(to=HandGuess.objects.get(guess=self.guess), user=self.user)
        except:
            self.fail('A valid vote triggered an exception')


    def test_vote_twice(self):
        '''
            Tries to vote twite to the same vote.
        '''
        with self.assertRaises(ValidationError):
            Vote.objects.create(to=HandGuess.objects.get(guess=self.guess), user=self.user)
            Vote.objects.create(to=HandGuess.objects.get(guess=self.guess), user=self.user)


    def test_vote_two_different_guesses_in_the_same_hand(self):
        '''
            Tries to vote two guesses from the same hand.
        '''
        with self.assertRaises(ValidationError):
            Vote.objects.create(to=HandGuess.objects.get(guess=self.guess), user=self.user)
            Vote.objects.create(to=HandGuess.objects.get(guess=self.secondary_guess), user=self.user)


    def test_vote_in_a_finished_hand(self):
        '''
            Tries to vote when a hand already ended.
        '''
        self.hand.finished_at = timezone.now()
        self.hand.save()
        with self.assertRaises(ValidationError):
            Vote.objects.create(to=HandGuess.objects.get(guess=self.guess), user=self.user)
