import random

class Letter:
    def __init__(self, letter: str, index: int = 0) -> None:
        self.letter: str = letter.lower()
        self.index: int = index
        self.in_word: bool = False
        self.in_correct_place: bool = False

    def mark_as_in_word(self) -> None:
        self.in_word = True

    def mark_as_in_correct_place(self) -> None:
        self.in_correct_place = True

    def is_in_word(self) -> bool:
        return self.in_word

    def is_in_correct_place(self) -> bool:
        return self.in_correct_place
    
# This cell has the tests your Letter class should pass in order to
# be evaluated as correct. Some of the tests you can see here and
# try on your own (press the button labeled validate on the toolbar).
# Others are hidden from your view, and will be evaluated only when
# you submit to the autograder.

# Check if the Letter class exists
assert "Letter" in dir(), "The Letter class does not exist, did you define it?"

# Check to see if the Letter class can be created
l: Letter
try:
    l = Letter("s")
except:
    assert (
        False
    ), "Unable to create a Letter object with Letter('s'), did you correctly define the Letter class?"

# Check to see if the Letter class has the in_correct_place attribute
assert hasattr(
    l, "in_correct_place"
), "The letter object created has no in_correct_place attribute, but this should be False by default. Did you create this attribute?"

class Bot:
    def __init__(self, word_list_filename: str) -> None:
        with open(word_list_filename, 'r') as file:
            self.word_list = [line.strip().lower() for line in file if len(line.strip()) == 5 and line.strip().isalpha()]

        random.shuffle(self.word_list)
        self.remaining_words = self.word_list.copy()
        self.guessed_words = set()
        self.correct_positions = [None] * 5
        self.eliminated_letters = set()

    def make_guess(self) -> str:
        for word in self.remaining_words:
            if word not in self.guessed_words:
                self.guessed_words.add(word)
                return word.upper()
        # Safe fallback to avoid invalid return
        return self.word_list[0].upper()

    def record_guess_results(self, guess: str, guess_results: list[Letter]) -> None:
        for letter in guess_results:
            if letter.is_in_correct_place():
                self.correct_positions[letter.index] = letter.letter
            elif not letter.is_in_word():
                self.eliminated_letters.add(letter.letter)

        new_remaining = []
        for word in self.remaining_words:
            if word in self.guessed_words:
                continue

            match = True
            for i, expected in enumerate(self.correct_positions):
                if expected and word[i] != expected:
                    match = False
                    break

            if match and any(ch in self.eliminated_letters for ch in word):
                match = False

            if match:
                new_remaining.append(word)

        self.remaining_words = new_remaining
        
# Tests for Bot class.

# Check if the Bot class exists
assert "Bot" in dir(), "The Bot class does not exist, did you define it?"

class GameEngine:
    """The GameEngine represents a new WordPy game to play."""

    def __init__(self):
        self.err_input = False
        self.err_guess = False
        self.prev_guesses = []  # record the previous guesses

    def play(
        self, bot, word_list_file: str = "words.txt", target_word: str = None
    ) -> None:
        """Plays a new game, using the supplied bot. By default the GameEngine
        will look in words.txt for the list of allowable words and choose one
        at random. Set the value of target_word to override this behavior and
        choose the word that must be guessed by the bot.
        """

        def format_results(results) -> str:
            """Small function to format the results into a string for quick
            review by caller.
            """
            response = ""
            for letter in results:
                if letter.is_in_correct_place():
                    response = response + letter.letter
                elif letter.is_in_word():
                    response = response + "*"
                else:
                    response = response + "?"
            return response

        def set_feedback(guess: str, target_word: str) -> tuple[bool, list[Letter]]:
            # whether the complete guess is correct
            # set it to True initially and then switch it to False if any letter doesn't match
            correct: bool = True

            letters = []
            for j in range(len(guess)):
                # create a new Letter object
                letter = Letter(guess[j])

                # check to see if this character is in the same position in the
                # guess and if so set the in_correct_place attribute
                if guess[j] == target_word[j]:
                    letter.in_correct_place = True
                    known_letters[j] = guess[j]  # record the known correct positions
                else:
                    # we know they don't have a perfect answer, so let's update
                    # our correct variable for feedback
                    correct = False

                # check to see if this character is anywhere in the word
                if guess[j] in target_word:
                    letter.in_word = True
                else:
                    unused_letters.add(guess[j])  # record the unused letters

                # add this letter to our list of letters
                letters.append(letter)

            return correct, letters

        # read in the dictionary of allowable words
        word_list: list(str) = list( # type: ignore
            map(lambda x: x.strip().upper(), open(word_list_file, "r").readlines())
        )
        # record the known correct positions
        known_letters: list(str) = [None, None, None, None, None] # type: ignore
        # set of unused letters
        unused_letters = set()

        # assign the target word to a member variable for use later
        if target_word is None:
            target_word = random.choice(word_list).upper()
        else:
            target_word = target_word.upper()
            if target_word not in word_list:
                print(f"Target word {target_word} must be from the word list")
                self.err_input = True
                return

        print(
            f"Playing a game of WordyPy using the word list file of {word_list_file}.\nThe target word for this round is {target_word}\n"
        )

        MAX_GUESSES = 6
        for i in range(1, MAX_GUESSES):
            # ask the bot for it's guess and evaluate
            guess: str = bot.make_guess()

            # print out a line indicating what the guess was
            print(f"Evaluating bot guess of {guess}")

            if guess not in word_list:
                print(f"Guessed word {guess} must be from the word list")
                self.err_guess = True
            elif guess in self.prev_guesses:
                print(f"Guess word cannot be the same one as previously used!")
                self.err_guess = True

            if self.err_guess:
                return

            self.prev_guesses.append(guess)  # record the previous guess

            for j, letter in enumerate(guess):
                if letter in unused_letters:
                    print(
                        f"The bot's guess used {letter} which was previously identified as not used!"
                    )
                    self.err_guess = True
                if known_letters[j] is not None:
                    if letter != known_letters[j]:
                        print(
                            f"Previously identified {known_letters[j]} in the correct position is not used at position {j}!"
                        )
                        self.err_guess = True

                if self.err_guess:
                    return

            # get the results of the guess
            correct, results = set_feedback(guess, target_word)

            # print out a line indicating whether the guess was correct or not
            print(f"Was this guess correct? {correct}")

            print(f"Sending guess results to bot {format_results(results)}\n")

            bot.record_guess_results(guess, results)

            # if they got it correct we can just end
            if correct:
                print(f"Great job, you found the target word in {i} guesses!")
                return

        # if we get here, the bot didn't guess the word
        print(
            f"Thanks for playing! You didn't find the target word in the number of guesses allowed."
        )
        return
    
class GameEngine:
    """The GameEngine represents a new WordPy game to play."""

    def __init__(self):
        self.err_input = False
        self.err_guess = False
        self.prev_guesses = []  # record the previous guesses

    def play(
        self, bot, word_list_file: str = "words.txt", target_word: str = None
    ) -> None:
        """Plays a new game, using the supplied bot. By default the GameEngine
        will look in words.txt for the list of allowable words and choose one
        at random. Set the value of target_word to override this behavior and
        choose the word that must be guessed by the bot.
        """

        def format_results(results) -> str:
            """Small function to format the results into a string for quick
            review by caller.
            """
            response = ""
            for letter in results:
                if letter.is_in_correct_place():
                    response = response + letter.letter
                elif letter.is_in_word():
                    response = response + "*"
                else:
                    response = response + "?"
            return response

        def set_feedback(guess: str, target_word: str) -> tuple[bool, list[Letter]]:
            # whether the complete guess is correct
            # set it to True initially and then switch it to False if any letter doesn't match
            correct: bool = True

            letters = []
            for j in range(len(guess)):
                # create a new Letter object
                letter = Letter(guess[j])

                # check to see if this character is in the same position in the
                # guess and if so set the in_correct_place attribute
                if guess[j] == target_word[j]:
                    letter.in_correct_place = True
                    known_letters[j] = guess[j]  # record the known correct positions
                else:
                    # we know they don't have a perfect answer, so let's update
                    # our correct variable for feedback
                    correct = False

                # check to see if this character is anywhere in the word
                if guess[j] in target_word:
                    letter.in_word = True
                else:
                    unused_letters.add(guess[j])  # record the unused letters

                # add this letter to our list of letters
                letters.append(letter)

            return correct, letters

        # read in the dictionary of allowable words
        word_list: list(str) = list( # type: ignore
            map(lambda x: x.strip().upper(), open(word_list_file, "r").readlines())
        )
        # record the known correct positions
        known_letters: list(str) = [None, None, None, None, None] # type: ignore
        # set of unused letters
        unused_letters = set()

        # assign the target word to a member variable for use later
        if target_word is None:
            target_word = random.choice(word_list).upper()
        else:
            target_word = target_word.upper()
            if target_word not in word_list:
                print(f"Target word {target_word} must be from the word list")
                self.err_input = True
                return

        print(
            f"Playing a game of WordyPy using the word list file of {word_list_file}.\nThe target word for this round is {target_word}\n"
        )

        MAX_GUESSES = 6
        for i in range(1, MAX_GUESSES):
            # ask the bot for it's guess and evaluate
            guess: str = bot.make_guess()

            # print out a line indicating what the guess was
            print(f"Evaluating bot guess of {guess}")

            if guess not in word_list:
                print(f"Guessed word {guess} must be from the word list")
                self.err_guess = True
            elif guess in self.prev_guesses:
                print(f"Guess word cannot be the same one as previously used!")
                self.err_guess = True

            if self.err_guess:
                return

            self.prev_guesses.append(guess)  # record the previous guess

            for j, letter in enumerate(guess):
                if letter in unused_letters:
                    print(
                        f"The bot's guess used {letter} which was previously identified as not used!"
                    )
                    self.err_guess = True
                if known_letters[j] is not None:
                    if letter != known_letters[j]:
                        print(
                            f"Previously identified {known_letters[j]} in the correct position is not used at position {j}!"
                        )
                        self.err_guess = True

                if self.err_guess:
                    return

            # get the results of the guess
            correct, results = set_feedback(guess, target_word)

            # print out a line indicating whether the guess was correct or not
            print(f"Was this guess correct? {correct}")

            print(f"Sending guess results to bot {format_results(results)}\n")

            bot.record_guess_results(guess, results)

            # if they got it correct we can just end
            if correct:
                print(f"Great job, you found the target word in {i} guesses!")
                return

        # if we get here, the bot didn't guess the word
        print(
            f"Thanks for playing! You didn't find the target word in the number of guesses allowed."
        )
        return
    
if __name__ == "__main__":
    # Chris's favorite words
    favorite_words = ["doggy", "drive", "daddy", "field", "state"]

    # Write this to a temporary file
    words_file = "temp_file.txt"
    with open(words_file, "w") as file:
        file.writelines("\n".join(favorite_words))

    # Initialize the student Bot
    bot = Bot(words_file)

    # Create a new GameEngine and play a game with the Bot, in this
    # test run I chose to set the target_word to "doggy"
    GameEngine().play(bot, word_list_file=words_file, target_word="field")