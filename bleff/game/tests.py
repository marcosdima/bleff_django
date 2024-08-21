import random
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from django.forms import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.contrib.auth.models import User

from .models import ConditionTag, Word, Language, Meaning, Game, Play, Hand, Guess, HandGuess, Vote, Choice, Condition
from . import utils

def create_word_meaning(word: str, language: Language, word_translation: str, content: str):
    word = Word.objects.create(word=word)

    return word, Meaning.objects.create(text=content, word_translation=word_translation, word=word, language=language)


def create_root_user():
    return User.objects.create_user(username="root_test", password="password")


def create_secondary_user():
    return User.objects.create_user(username='second', password='1234')


def create_basic_language():
    tag = 'EN'
    name = 'English'
    return Language.objects.create(tag=tag, name=name)


def login_root_user(test: TestCase):
    test.client.login(username="root_test", password="password")


def login_secondary_user(test: TestCase):
    test.client.login(username='second', password='1234')


def create_user_and_play(username: str, password: str, game: Game):
    user = User.objects.create(username=username, password=password)
    Play.objects.create(user=user, game=game)
    return user


def create_n_players(n: int, game: Game):
    return [create_user_and_play(username=f'TestUser °{i}', password=f'{str(i) * 3}', game=game) for i in range(n)]


def create_condition_tag(tag: str, max: int = 4, min: int = 4) -> ConditionTag:
    return ConditionTag.objects.create(tag=tag, max=max, min=min)


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
    def setUp(self):
        self.lang = Language.objects.create(tag='EN', name='English')


    def test_create_a_meaning(self):
        word_text = 'House'
        content = 'A place where you live.'
        _, meaning = create_word_meaning(word=word_text, language=self.lang, word_translation=word_text, content=content)

        try:
            meaning.full_clean() 
        except ValidationError:
            self.fail("Valid Meaning raised ValidationError")


    def test_create_a_meaning_with_word_translation_field_as_an_empty_string(self):
        '''
            Create a new meaning with empty strings as word_translation.
        '''
        word_text = ''
        content = 'A place where you live.'
        _, meaning = create_word_meaning(word=word_text, language=self.lang, word_translation=word_text, content=content)

        with self.assertRaises(ValidationError):
           meaning.full_clean()


    def test_create_a_meaning_with_content_field_as_an_empty_string(self):
        '''
            Create a new meaning with empty strings as content.
        '''
        word_text = 'House'
        content = ''
        _, meaning = create_word_meaning(word=word_text, language=self.lang, word_translation=word_text, content=content)

        with self.assertRaises(ValidationError):
           meaning.full_clean()


    def test_create_a_meaning_duplicated(self):
        word = Word.objects.create(word='House')
        content = 'A place where you live.'
        Meaning.objects.create(text=content, word_translation='House', word=word, language=self.lang)
        
        with self.assertRaises(IntegrityError):
           Meaning.objects.create(text=content, word_translation='House', word=word, language=self.lang)


    def test_meaning_str_function(self):
        word_text = 'House'
        content = 'A place where you live.'
        _, meaning = create_word_meaning(word=word_text, language=self.lang, word_translation=word_text, content=content)
        self.assertEqual(f'{word_text}: {content}', meaning.__str__(), 'Str function does not works!')


class GameModelTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
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


    def test_set_game_as_finished(self):
        '''
            Tests if its possible to set a game as finished.
        '''
        game = Game.objects.create(creator=self.user, idiom=self.lang)
        game.end()

        gameAfterEnd = Game.objects.get(id=game.id)
        self.assertFalse(gameAfterEnd.finished_at == None)


    def test_set_game_as_finished(self):
        '''
            Tests if its possible to set a game as finished twice.
        '''
        game = Game.objects.create(creator=self.user, idiom=self.lang)
        game.end()

        with self.assertRaises(ValidationError):
            gameAfterEnd = Game.objects.get(id=game.id)
            gameAfterEnd.end()


class PlayModelTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
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
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)

        self.words = ['Cow', 'Diary', 'Python', 'Goose', 'Cheese']
        for word in self.words:
            create_word_meaning(word=word, language=self.lang, content=f'An explanation of what "{word}" is in English.', word_translation=word)

        self.word = Word.objects.get(word=self.words[0])
        self.word_2 = Word.objects.get(word=self.words[1])


    def test_create_a_new_hand(self):
        '''
            Create a new hand with valid data.
        '''
        try:
            Hand.objects.create(game=self.game, leader=self.user)
        except ValidationError or IntegrityError:
            self.fail("Valid Hand raised an error")


    def test_create_a_new_hand_with_no_leader(self):
        '''
            Create a new hand without 'leader'. The leader should be setted by default as the game creator (Beacuase is the only player)
        '''
        hand = Hand.objects.create(game=self.game)
        self.assertEqual(self.game.creator.id, hand.leader.id)

            
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
        hand = Hand.objects.create(game=self.game, leader=self.user, word=self.word)
        hand.end()
        self.assertEqual(hand.finished_at, Hand.objects.get(id=hand.id).finished_at)


    def test_finish_hand_before_started(self):
        '''
            Tries to set a finishing time that happend before the starting time.
        '''
        with self.assertRaises(ValidationError):
            hand = Hand.objects.create(game=self.game, leader=self.user, word=self.word)
            hand.finished_at = timezone.now() - timedelta(days=1)
            hand.save()


    def test_hand_can_not_be_created_if_there_is_another_unfinished(self):
        '''
            A hand can't be created if exists another with finished_at as None.
        '''
        Hand.objects.create(game=self.game, leader=self.user, word=self.word)
        
        with self.assertRaises(ValidationError):
            Hand.objects.create(game=self.game, leader=self.user, word=self.word_2)


    def test_hand_leader_default_setter_rotates_players(self):
        '''
            The leader changes every hand.
        '''
        Play.objects.create(game=self.game, user=self.secondaryUser)

        first = Hand.objects.create(game=self.game, leader=self.user)
        first.end()
        
        second = Hand.objects.create(game=self.game, word=self.word_2)
        self.assertEqual(second.leader.id, self.secondaryUser.id)


    def test_set_default_choice(self):
        '''
            Test if the default creation of choice works.
        '''
        hand = Hand.objects.create(game=self.game)
        words = [c.word for c in Choice.objects.filter(hand=hand)]
        self.assertEqual(len(words), len(self.words))

        for word in words:
            self.assertTrue(word.word in self.words)


    def test_set_default_choice_when_exists_a_previus_hand(self):
        '''
            Test if the default creation of choice works when a word was selected in a previus hand.
        '''
        index = random.randint(0, len(self.words) - 1)
        word = Word.objects.get(word=self.words[index])
        hand = Hand.objects.create(game=self.game)

        hand.word = word
        hand.save()
        hand.end()

        secondHand = Hand.objects.create(game=self.game)
        choice_values = Choice.objects.filter(hand=secondHand)

        self.assertEqual(len(choice_values), len(self.words) - 1)
        self.assertFalse(self.words[index] in choice_values)
        

    def test_hand_word_set(self):
        '''
            Sets the hand word.
        '''
        hand = Hand.objects.create(game=self.game)
        hand.word = self.word
        hand.save()

        
    def test_hand_word_set_twice(self):
        '''
            Sets the hand word twice, not permited.
        '''
        hand = Hand.objects.create(game=self.game)
        hand.word = self.word
        hand.save()

        with self.assertRaises(ValidationError):
            hand.word = self.word_2
            hand.save()


    def test_set_word_without_its_choice(self):
        '''
            Tries to create a hand with a word that does not have 'choice'.
        '''
        hand = Hand.objects.create(game=self.game)

        with self.assertRaises(ValidationError):
            hand.word = Word.objects.create(word='DoesNotExists')
            hand.save()


    def test_create_hand_in_finished_game(self):
        '''
            If a game ended, then more hands can not be created.
        '''
        self.game.end()
        
        with self.assertRaises(ValidationError):
            Hand.objects.create(game=self.game).full_clean()


class GuessModelTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)
        self.word, self.meaning = create_word_meaning('House', language=self.lang, content='An explanation of what "HOUSE" is in English.', word_translation='HoUsE')
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


    def test_create_a_default_guess_after_create_hand(self):
        '''
            When a Hand is created and has a word, a Guess with the right content has to be created too.
        '''
        # In 'setUp' self.hand was created.
        right = Guess.objects.filter(hand=self.hand)[0]
        self.assertTrue(right != None)
        self.assertTrue(right.is_original)


    def test_create_a_default_guess_after_create_hand_but_there_is_no_word(self):
        '''
            When a Hand is created and has a word, a Guess with the right content has to be created too. But in this case there is no word selected, so it can not happend.
        '''
        self.hand.end()
        hand = Hand.objects.create(game=self.game)
        self.assertFalse(Guess.objects.filter(hand=hand).exists())


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


    def test_create_a_guess_but_hand_ended(self):
        '''
            If hand ended, then guesses can not be created.
        '''
        self.hand.end()
        with self.assertRaises(ValidationError):
            Guess.objects.create(hand=self.hand, content=self.content, writer=self.secondaryUser).full_clean()


class HandGuessModelTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)
        self.word, self.meaning = create_word_meaning('House', language=self.lang, content='An explanation of what "HOUSE" is in English.', word_translation='HoUsE')
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
            Check if is_correct field has the value None by default.
        '''
        guess = Guess.objects.create(hand=self.hand, content=self.content, writer=self.user)
        self.assertEqual(None, HandGuess.objects.get(hand=self.hand, guess=guess).is_correct)


    def test_is_correct_can_be_changed(self):
        '''
            Change the value of is correct.
        '''
        guess = Guess.objects.create(hand=self.hand, writer=self.user)
        handguess = HandGuess.objects.get(hand=self.hand, guess=guess)
        self.assertEqual(None, handguess.is_correct)
        
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
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)
        self.word, self.meaning = create_word_meaning('House', language=self.lang, content='An explanation of what "HOUSE" is in English.', word_translation='HoUsE')
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


class ChoiceModelTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)
        self.hand = Hand.objects.create(leader=self.user, game=self.game)
        self.word, self.meaning = create_word_meaning('House', language=self.lang, content='An explanation of what "HOUSE" is in English.', word_translation='HoUsE')
        self.word_2, self.meaning_2 = create_word_meaning('Dou', language=self.lang, content='An explanation of what "DOU" is in English.', word_translation='DoU')


    def test_create_choice(self):
        '''
            Test choice creation.
        '''
        try:
            Choice.objects.create(hand=self.hand, word=self.word)
        except:
            self.fail('Valid choice could not be created.')


    def test_create_choice_twice(self):
        '''
            Test cretion of two choice with the same hand and word.
        '''
        Choice.objects.create(hand=self.hand, word=self.word)
        with self.assertRaises(IntegrityError):
            Choice.objects.create(hand=self.hand, word=self.word)


    def test_create_choice_with_a_played_word(self):
        '''
            Test creation of choice with a played word.
        '''
        Choice.objects.create(hand=self.hand, word=self.word)
        self.hand.word = self.word
        self.hand.end()

        secondHand = Hand.objects.create(game=self.game)
        with self.assertRaises(ValidationError):
            Choice.objects.create(hand=secondHand, word=self.word)
            

    def test_create_a_new_choice_with_a_word_without_meaning(self):
        '''
            Create a new choice with a word with no meaning in the Game idiom.
        '''
        anyWord = Word.objects.create(word='AnyWord')

        with self.assertRaises(ValidationError):
            Choice.objects.create(hand=self.hand, word=anyWord)


class UtilsFunctionsTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)

        self.words = ['Cow', 'Diary', 'Python', 'Goose', 'Cheese']
        for word in self.words:
            create_word_meaning(word=word, language=self.lang, content=f'An explanation of what "{word}" is in English.', word_translation=word)

        self.word = Word.objects.get(word=self.words[0])
        self.word_2 = Word.objects.get(word=self.words[1])

        self.max = create_condition_tag(tag='MAX_PLAYERS')
        self.min = create_condition_tag(tag='MIN_PLAYERS')
    

    def test_plays_game_function_should_be_true(self):
        '''
            This function should say if a player plays a game.
        '''
        self.assertTrue(utils.plays_game(self.user, self.game.id))


    def test_plays_game_function_should_be_false(self):
        '''
            This function should say if a player plays a game.
        '''
        self.assertFalse(utils.plays_game(self.secondaryUser, self.game.id))

    
    def test_is_leader_function_should_be_true(self):
        '''
            This function should say if a player is a hand leader.
        '''
        Hand.objects.create(game=self.game)
        self.assertTrue(utils.is_leader(self.user, self.game.id))


    def test_is_leader_function_should_be_false(self):
        '''
            This function should say if a player is a hand leader.
        '''
        Hand.objects.create(game=self.game)
        self.assertFalse(utils.is_leader(self.secondaryUser, self.game.id))


    def test_get_hand_function(self):
        '''
            This function should return the current hand.
        '''
        hand = Hand.objects.create(game=self.game)
        self.assertEqual(hand, utils.get_game_hand(game_id=self.game.id))


    def test_get_hand_function_with_two_hands(self):
        '''
            This function should return the current hand.
        '''
        hand = Hand.objects.create(game=self.game)
        hand.end()

        second_hand = Hand.objects.create(game=self.game)
        self.assertEqual(second_hand, utils.get_game_hand(game_id=self.game.id))


    def test_get_hand_function_with_no_hands(self):
        '''
            This function should return the current hand.
        '''
        self.assertEqual(None, utils.get_game_hand(game_id=self.game.id))


    def test_get_hand_choice_words(self):
        '''
            Test 'get_hand_choice_words' function
        '''
        hand = Hand.objects.create(game=self.game)
        for w in utils.get_hand_choice_words(hand):
            self.assertTrue(w.word in self.words)


    def test_get_hand_choice_words_after_a_word_was_used(self):
        '''
            Test 'get_hand_choice_words' function when a word was used before in the game.
        '''
        hand = Hand.objects.create(game=self.game)
        word_target = utils.get_hand_choice_words(hand)[0]
        hand.word = word_target
        hand.save()
        hand.end()

        second_hand = Hand.objects.create(game=self.game)
        choices = utils.get_hand_choice_words(second_hand)
        for w in choices:
            self.assertTrue(w.word in self.words)

        self.assertFalse(word_target in choices)


    def test_remove_fields(self):
        '''
            This function should receive a Model and some fields to remove and return a dictionary without the removed fields.
        '''
        languages_without_tag = utils.remove_fields(object=Language, fields=['tag'], filters={'tag': self.lang.tag})

        for language in languages_without_tag:
            self.assertEqual(self.lang.name, language.name)
            self.assertFalse(hasattr(language, 'tag'))


    def test_remove_fields_with_non_existent_field(self):
        '''
            The object should remain the same as before remove fields.
        '''
        languages_without_false_field = utils.remove_fields(object=Language, fields=['FalseField'], filters={'tag': self.lang.tag})

        for language in languages_without_false_field:
            self.assertEqual(self.lang.name, language.name)
            self.assertEqual(self.lang.tag, language.tag)


    def test_conditions_are_met(self):
        '''
            conditions_are_met function should validate that the conditions, if exists, are met.
        '''
        Condition.objects.create(game=self.game, tag=self.max, value=4)
        Condition.objects.create(game=self.game, tag=self.min, value=4)
        create_n_players(n=3, game=self.game)
        self.assertEqual(len(utils.conditions_are_met(game_id=self.game.id)), 0)


    def test_conditions_are_met_with_no_conditions(self):
        '''
            There are no conditions, so conditions are met.
        '''
        self.assertEqual(len(utils.conditions_are_met(game_id=self.game.id)), 0)


    def test_conditions_are_not_enough_players(self):
        '''
            There is a condition of 10 players min, so conditions are not met.
        '''
        Condition.objects.create(game=self.game, tag=self.min, value=self.min.min)
        self.assertEqual(len(utils.conditions_are_met(game_id=self.game.id)), 1)


    def test_conditions_are_not_enough_players(self):
        '''
            There is a condition of 10 players min, so conditions are not met.
        '''
        Condition.objects.create(game=self.game, tag=self.max, value=self.min.min)
        create_n_players(n=10, game=self.game)
        self.assertEqual(len(utils.conditions_are_met(game_id=self.game.id)), 1)


    def test_is_leader(self):
        '''
            Is leader function should return True.
        '''
        Hand.objects.create(game=self.game)
        self.assertTrue(utils.is_leader(user=self.user, game_id=self.game.id))


    def test_is_leader_but_is_not_the_leader(self):
        '''
            Is leader function should return False.
        '''
        Hand.objects.create(game=self.game)
        Play.objects.create(game=self.game, user=self.secondaryUser)
        self.assertFalse(utils.is_leader(user=self.secondaryUser, game_id=self.game.id))


    def test_there_are_guesses_to_check(self):
        '''
            With no guesses should be false.
        '''
        self.assertFalse(utils.there_are_guesses_to_check(game_id=self.game.id))


    def test_there_are_guesses_to_check_but_there_are(self):
        '''
            With no guesses should be true.
        '''
        hand = Hand.objects.create(game=self.game)
        hand.word = self.word
        hand.save()

        Guess.objects.create(writer=self.user, content='CONTENT A CONTENT A CONTENT', hand=hand)

        self.assertTrue(utils.there_are_guesses_to_check(game_id=self.game.id))


    def test_votes_remaining(self):
        '''
            This function should return the number of votes remaining.
        '''
        Play.objects.create(game=self.game, user=self.secondaryUser)
        content = 'aaaaaaaaaaaaaaaaaaaaaaaaa'
        hand = Hand.objects.create(game=self.game)
        Guess.objects.create(content=content, writer=self.user, hand=hand)

        self.assertEqual(utils.votes_remaining(game_id=self.game.id), 1)


    def test_votes_remaining_after_vote(self):
        '''
            This function should return the number of votes remaining.
        '''
        Play.objects.create(game=self.game, user=self.secondaryUser)
        content = 'aaaaaaaaaaaaaaaaaaaaaaaaa'
        hand = Hand.objects.create(game=self.game, word=self.word)
        guess = Guess.objects.create(content=content, writer=self.user, hand=hand)
        hg = HandGuess.objects.get(hand=hand, guess=guess)
        hg.is_correct = False
        hg.save()
        
        Vote.objects.create(user=self.user, to=hg)
        self.assertEqual(utils.votes_remaining(game_id=self.game.id), 0)


    def test_already_vote(self):
        '''
            This function should return True if user already vote.
        '''
        content = 'aaaaaaaaaaaaaaaaaaaaaaaaa'
        hand = Hand.objects.create(game=self.game, word=self.word)
        guess = Guess.objects.create(content=content, writer=self.user, hand=hand)
        hg = HandGuess.objects.get(hand=hand, guess=guess)
        hg.is_correct = False
        hg.save()
        
        Vote.objects.create(user=self.user, to=hg)
        self.assertTrue(utils.already_vote(user=self.user, game_id=self.game.id))


    def test_already_vote(self):
        '''
            This function should return False if user does not vote yet.
        '''
        content = 'aaaaaaaaaaaaaaaaaaaaaaaaa'
        hand = Hand.objects.create(game=self.game, word=self.word)
        guess = Guess.objects.create(content=content, writer=self.user, hand=hand)
        hg = HandGuess.objects.get(hand=hand, guess=guess)
        hg.is_correct = False
        hg.save()

        self.assertFalse(utils.already_vote(user=self.user, game_id=self.game.id))


    def test_last_hand(self):
        '''
            Should return last hand played.
        '''
        hand = Hand.objects.create(game=self.game)
        self.assertEqual(hand.id, utils.last_hand(game_id=self.game.id).id)

    
    def test_last_hand_with_a_finished_hand(self):
        '''
            Should return last hand played.
        '''
        hand = Hand.objects.create(game=self.game)
        hand.end()

        self.assertEqual(hand.id, utils.last_hand(game_id=self.game.id).id)


    def test_last_hand_with_a_new_one(self):
        '''
            Should return last hand played.
        '''
        hand = Hand.objects.create(game=self.game)
        hand.end()
        second_hand = Hand.objects.create(game=self.game)
        self.assertEqual(second_hand.id, utils.last_hand(game_id=self.game.id).id)


class GameViewTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.lang = create_basic_language()


    def test_games(self):
        '''
            The view should display a list of available games.
        '''
        game = Game.objects.create(creator=self.user, idiom=self.lang)
        response = self.client.get(reverse('game:index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No games are available.")
        self.assertQuerySetEqual(response.context["object_list"], [game])


    def test_no_games(self):
        '''
            The view should display a no-games message.
        '''
        response = self.client.get(reverse('game:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games are available.")
        self.assertQuerySetEqual(response.context["object_list"], [])


class EnterGameViewTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.lang = create_basic_language()
        self.secondaryUser = create_secondary_user()
        self.game = Game.objects.create(creator=self.user, idiom=self.lang)

    
    def test_enter_game(self):
        '''
            This shouldn't create a play, because by default it's created for the game creator, and redirect the user to waiting.
        '''
        self.assertEqual(Play.objects.filter(game=self.game).count(), 1)

        login_root_user(self)
        response = self.client.post(path=reverse('game:enter_game'), data={'game': self.game.id})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:waiting', args=[self.game.id]))

        self.assertEqual(Play.objects.filter(game=self.game).count(), 1)
        

    def test_enter_game_not_as_creator(self):
        '''
            This should create a play with this user and redirect the user to waiting.
        '''
        login_secondary_user(self)
        response = self.client.post(path=reverse('game:enter_game'), data={'game': self.game.id})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(f'/game/{self.game.id}/'))
        self.assertEqual(Play.objects.filter(game=self.game).count(), 2)


class CreateGameViewTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.lang = create_basic_language()
        self.secondaryUser = create_secondary_user()
        self.max = create_condition_tag(tag='MAX_PLAYERS', max=8, min=4)
        self.min = create_condition_tag(tag='MIN_PLAYERS', max=10, min=4)

    
    def test_create_a_game(self):
        '''
            An user tries to create a game.
        '''
        login_root_user(self)
        data = {'language': self.lang.tag, self.max.tag: self.max.min, self.min.tag: self.min.min, }
        response = self.client.post(path=reverse('game:create'), data=data)
        game = Game.objects.all()[0]

        self.assertEqual(response.url, reverse('game:waiting', args=[game.id]))


    def test_create_a_game_but_you_are_already_playing(self):
        '''
            An user tries to create a game.
        '''
        login_root_user(self)
        game = Game.objects.create(idiom=self.lang, creator=self.user)
        self.assertEqual(Game.objects.all().count(), 1)

        data = {'language': self.lang.tag, self.max.tag: self.max.min, self.min.tag: self.min.min, }
        response = self.client.post(path=reverse('game:create'), data=data)
        self.assertEqual(Game.objects.all().count(), 1)
        self.assertEqual(response.url, reverse('game:waiting', args=[game.id]))


    def test_create_a_game_but_conditions_contradiction(self):
        '''
            If MIN_PLAYERS has a value grater than MAX_PLAYERS, then should raise a validation error.
        '''
        login_root_user(self)
        data = {'language': self.lang.tag, self.max.tag: self.max.min, self.min.tag: 9, }
        response = self.client.post(path=reverse('game:create'), data=data)

        self.assertEqual(Game.objects.all().count(), 0)
        self.assertEqual(response.url, reverse('game:index'))


class WaitingViewTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)


    def test_waiting_view(self):
        '''
            The view should display a list with one element, the game creator.
        '''
        login_root_user(self)

        response = self.client.get(reverse('game:waiting', args=[self.game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["users"], [self.user.username])


    def test_waiting_view_with_two_players(self):
        '''
            The view should display a list with game users.
        '''
        login_secondary_user(self)
        Play.objects.create(game=self.game, user=self.secondaryUser)

        response = self.client.get(reverse('game:waiting', args=[self.game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["users"], [self.user.username, self.secondaryUser.username])

    
    def test_waiting_view_with_no_login(self):
        '''
            The view should redirect you to login view.
        '''
        response = self.client.get(reverse('game:waiting', args=[self.game.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/users/login/'))


class StartGameViewTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)


    def test_start_game_view(self):
        '''
            The view should create the first hand and redirect the user to hand view.
        '''
        login_root_user(self)
        response = self.client.post(reverse('game:start_game', args=[self.game.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:hand', args=[self.game.id]))
        self.assertEqual(Hand.objects.filter(game=self.game).count(), 1)


    def test_start_game_view_but_your_are_not_the_creator(self):
        '''
            The view should redirect the user to waiting.
        '''
        Play.objects.create(game=self.game, user=self.secondaryUser)
        login_secondary_user(self)
        
        response = self.client.post(reverse('game:start_game', args=[self.game.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url, reverse('game:waiting', args=[self.game.id]))
        self.assertEqual(Hand.objects.filter(game=self.game).count(), 0)


    def test_start_game_view_but_creator_is_null(self):
        '''
            The view should create the first hand and redirect the user to hand view.
        '''
        Play.objects.create(game=self.game, user=self.secondaryUser)

        self.game.creator = None
        self.game.save()

        login_secondary_user(self)
        response = self.client.post(reverse('game:start_game', args=[self.game.id]))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:hand', args=[self.game.id]))
        self.assertEqual(Hand.objects.filter(game=self.game).count(), 1)


    def test_start_game_view_but_your_are_not_playing(self):
        '''
            The view should create the first hand and redirect the user to hand view.
        '''
        login_secondary_user(self)
        response = self.client.post(reverse('game:start_game', args=[self.game.id]))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:index'))
        self.assertEqual(Hand.objects.filter(game=self.game).count(), 0)


    def test_start_game_but_conditions_are_not_met(self):
        '''
            The game does not met the conditions setted, so should stay in waiting 
        '''
        login_root_user(self)
        Condition.objects.create(game=self.game, tag=create_condition_tag(tag="MIN_PLAYERS"), value=4)
        response = self.client.post(reverse('game:start_game', args=[self.game.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:waiting', args=[self.game.id]))


class HandViewTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)

        self.words = ['Cow', 'Diary', 'Python', 'Goose', 'Cheese']
        for word in self.words:
            create_word_meaning(word=word, language=self.lang, content=f'An explanation of what "{word}" is in English.', word_translation=word)

        self.word = Word.objects.get(word=self.words[0])
        self.word_2 = Word.objects.get(word=self.words[1])


    def test_hand_view_as_leader(self):
        '''
            This view should display a list of words to choose.
        '''
        login_root_user(self)
        Hand.objects.create(game=self.game, leader=self.user)
        response = self.client.get(path=reverse('game:hand', args=[self.game.id]))
        self.assertEqual(response.status_code, 200)

        for word in self.words:
            self.assertContains(response, self.word.word)


    def test_hand_view_as_not_leader(self):
        '''
            This view should display a message.
        '''
        Play.objects.create(game=self.game, user=self.secondaryUser)
        login_secondary_user(self)
        hand = Hand.objects.create(game=self.game, leader=self.user)
        response = self.client.get(path=reverse('game:hand', args=[self.game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.words.__str__())
        self.assertContains(response, f'Waiting {hand.leader} to choose a word')

    
    def test_hand_view_but_you_do_not_playing_a_game(self):
        '''
            This view should display a message.
        '''
        login_secondary_user(self)
        Hand.objects.create(game=self.game, leader=self.user)
        response = self.client.get(path=reverse('game:hand', args=[self.game.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:index'))


    def test_hand_view_with_chosen_word(self):
        '''
            If a word was chosen, then even the leader should not have word to choose.
        '''
        login_root_user(self)
        hand = Hand.objects.create(game=self.game, leader=self.user)
        hand.word = self.word

        response = self.client.get(path=reverse('game:hand', args=[self.game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.words.__str__())


class ChooseViewTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)

        self.words = ['Cow', 'Diary', 'Python', 'Goose', 'Cheese']
        for word in self.words:
            create_word_meaning(word=word, language=self.lang, content=f'An explanation of what "{word}" is in English.', word_translation=word)

        self.word = Word.objects.get(word=self.words[0])
        self.word_2 = Word.objects.get(word=self.words[1])

        self.hand = Hand.objects.create(game=self.game, leader=self.user)


    def test_choose_a_word(self):
        '''
            Choose the hand word.
        '''
        login_root_user(self)
        response = self.client.post(path=reverse('game:choose', args=[self.game.id]), data={'choice': self.word.word})

        self.assertEqual(response.url, reverse('game:hand', args=[self.game.id]))
        self.assertEqual(Hand.objects.get(id=self.hand.id).word, self.word)


    def test_choose_a_word_but_you_are_not_the_leader(self):
        '''
            Only the leader can choose.
        '''
        Play.objects.create(game=self.game, user=self.secondaryUser)
        login_secondary_user(self)
        response = self.client.post(path=reverse('game:choose', args=[self.game.id]), data={'choice': self.word.word})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:hand', args=[self.game.id]))
        self.assertEqual(Hand.objects.get(id=self.hand.id).word, None)


    def test_choose_a_word_but_you_are_not_playing(self):
        '''
            If you are not playing any game, then it should send you to index.
        '''
        login_secondary_user(self)
        response = self.client.post(path=reverse('game:choose', args=[self.game.id]), data={'choice': self.word.word})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:index'))
        self.assertEqual(Hand.objects.get(id=self.hand.id).word, None)

    
    def test_choose_a_word_but_you_are_not_playing_this_game(self):
        '''
            If you are not playing this game, then it should send you to your game (In This case the user's game is in waiting state).
        '''
        other_game = Game.objects.create(creator=self.secondaryUser, idiom=self.lang)
        Play(game=other_game, user=self.secondaryUser)
        login_secondary_user(self)
        response = self.client.post(path=reverse('game:choose', args=[self.game.id]), data={'choice': self.word.word})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:waiting', args=[other_game.id]))
        self.assertEqual(Hand.objects.get(id=self.hand.id).word, None)


class MakeGuessViewTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)

        self.words = ['Cow', 'Diary', 'Python', 'Goose', 'Cheese']
        for word in self.words:
            create_word_meaning(word=word, language=self.lang, content=f'An explanation of what "{word}" is in English.', word_translation=word)

        self.word = Word.objects.get(word=self.words[0])
        self.word_2 = Word.objects.get(word=self.words[1])

        self.hand = Hand.objects.create(game=self.game, leader=self.user)
        self.hand.word = self.word
        self.hand.save()

    
    def test_make_a_guess_as_leader(self):
        '''
            The leader make a guess.
        '''
        Play.objects.create(user=self.secondaryUser, game=self.game)
        login_root_user(self)
        guess_text = 'I think that means something like...'
        response = self.client.post(path=reverse('game:make_guess', args=[self.game.id]), data={'guess': guess_text})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:check_guesses', args=[self.game.id]))
        self.assertEqual(len(Guess.objects.all()), 2)


    def test_make_a_guess_as_player(self):
        '''
            An user make a guess.
        '''
        Play.objects.create(user=self.secondaryUser, game=self.game)
        login_secondary_user(self)
        guess_text = 'I think that means something like...'
        response = self.client.post(path=reverse('game:make_guess', args=[self.game.id]), data={'guess': guess_text})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:guesses', args=[self.game.id]))
        self.assertEqual(len(Guess.objects.all()), 2)


    def test_make_a_guess_but_there_are_not_playing(self):
        '''
            An user make a guess.
        '''
        login_secondary_user(self)
        guess_text = 'I think that means something like...'
        response = self.client.post(path=reverse('game:make_guess', args=[self.game.id]), data={'guess': guess_text})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:index'))


class CheckGuessesViewTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)

        self.words = ['Cow', 'Diary', 'Python', 'Goose', 'Cheese']
        for word in self.words:
            create_word_meaning(word=word, language=self.lang, content=f'An explanation of what "{word}" is in English.', word_translation=word)

        self.word = Word.objects.get(word=self.words[0])
        self.word_2 = Word.objects.get(word=self.words[1])

        self.hand = Hand.objects.create(game=self.game, leader=self.user)
        self.hand.word = self.word
        self.hand.save()
  
        self.root_guess = Guess.objects.create(writer=self.user, content='A content sdasdasdasdasda', hand=self.hand)


    def test_check_guesses(self):
        '''
            Get to check_guesses.
        '''
        login_root_user(self)
        response = self.client.get(reverse('game:check_guesses', args=[self.game.id]))
        
        self.assertContains(response=response, text= 'Check guesses', status_code=200)


    def test_check_guesses_but_you_are_not_the_leader(self):
        '''
            Get to check_guesses.
        '''
        Play.objects.create(game=self.game, user=self.secondaryUser)
        Guess.objects.create(writer=self.secondaryUser, content='A content sdasdasdasdasda 2', hand=self.hand)

        login_secondary_user(self)
        
        response = self.client.get(reverse('game:check_guesses', args=[self.game.id]))
        
        self.assertEqual(response.url, reverse('game:guesses', args=[self.game.id]))


    def test_check_guesses_post(self):
        '''
            Get to check_guesses.
        '''
        login_root_user(self)

        data = {
            self.root_guess.id: False 
        }
        response = self.client.post(reverse('game:check_guesses', args=[self.game.id]), data=data)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:hand_detail', args=[self.game.id]))
        self.assertEqual(HandGuess.objects.filter(hand=self.hand, is_correct=False).count(), 2)


    def test_check_guesses_post_but_removing(self):
        '''
            Get to check_guesses.
        '''
        login_root_user(self)

        data = {
            self.root_guess.id: True 
        }
        response = self.client.post(reverse('game:check_guesses', args=[self.game.id]), data=data)
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:hand_detail', args=[self.game.id]))
        self.assertEqual(HandGuess.objects.filter(hand=self.hand, is_correct=False).count(), 1)


class VoteViewTest(TestCase):
    def setUp(self):
        self.user = create_root_user()
        self.secondaryUser = create_secondary_user()
        self.lang = create_basic_language()
        self.game = Game.objects.create(idiom=self.lang, creator=self.user)
        Play.objects.create(game=self.game, user=self.secondaryUser)

        self.words = ['Cow', 'Diary', 'Python', 'Goose', 'Cheese']
        for word in self.words:
            create_word_meaning(word=word, language=self.lang, content=f'An explanation of what "{word}" is in English.', word_translation=word)

        self.word = Word.objects.get(word=self.words[0])
        self.word_2 = Word.objects.get(word=self.words[1])

        self.hand = Hand.objects.create(game=self.game, leader=self.user)
        self.hand.word = self.word
        self.hand.save()
  
        self.root_guess = Guess.objects.create(writer=self.user, content='A content sdasdasdasdasda', hand=self.hand)
        self.secondary_guess = Guess.objects.create(writer=self.secondaryUser, content='A content sdasdasdasdasda 2', hand=self.hand)

        # To vote, first should be checked.
        data = {
            self.root_guess.id: False,
            self.secondary_guess.id: False
        }
        login_root_user(self)
        self.client.post(reverse('game:check_guesses', args=[self.game.id]), data=data)

    
    def test_vote_your_guess(self):
        '''
            Should let you vote.
        '''
        login_secondary_user(self)
        response = self.client.post(path=reverse('game:vote', args=[self.game.id]), data={'guess': self.secondary_guess.id})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:hand_detail', args=[self.hand.id]))
        self.assertEqual(Vote.objects.all().count(), 1)

    
    def test_vote_your_guess_but_you_are_the_leader(self):
        '''
            Shouldn't let you vote.
        '''
        login_root_user(self)
        response = self.client.post(path=reverse('game:vote', args=[self.game.id]), data={'guess': self.secondary_guess.id})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('game:hand_detail', args=[self.hand.id]))
        self.assertEqual(Vote.objects.all().count(), 0)
