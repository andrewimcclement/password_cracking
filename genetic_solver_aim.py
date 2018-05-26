# -*- coding: utf-8 -*-
"""
Created on Fri May 25 19:42:38 2018
"""

__author__ = "Andrew I McClement"

from random import random, randint, sample
from time import sleep

from evaluator import PasswordChecker
from evaluator import get_random_letter
from evaluator import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH


class SolvedException(Exception):
    def __init__(self, solution):
        self.solution = solution


class GeneticSolver:

    def __init__(self,
                 mutation_rate: float=0.05,
                 length_shift: int=6,
                 survival_rate: float=0.4,
                 random_survival_rate: float=0.1):
        self._parent_generation = set()
        self._child_generation = set()

        self._mutation_rate = mutation_rate
        self._length_shift = length_shift
        self._survival_rate = survival_rate
        self._random_rate = random_survival_rate

    def solve(self, checker: PasswordChecker) -> str:
        """ Solve for the password.

        Uses checker to validate guesses.
        """

        self._generate_first_generation((MAX_PASSWORD_LENGTH
                                         + MIN_PASSWORD_LENGTH)/2)

        good_to_keep = int(len(self._child_generation) * self._survival_rate)
        good_to_keep = max(2, good_to_keep)
        random_to_keep = int(len(self._child_generation) * self._random_rate)
        random_to_keep = max(1, random_to_keep)
        assert good_to_keep + random_to_keep < len(self._child_generation)

        previous_scores = [(self._get_score(guess, checker), guess)
                           for guess in self._parent_generation]

        while True:
            try:
                new_scores = [(self._get_score(guess, checker), guess)
                              for guess in self._child_generation]
            except SolvedException as e:
                return e.solution

            scores = new_scores + previous_scores
            scores.sort(reverse=True)

            good_guesses = scores[:good_to_keep]
            randoms = sample(scores[good_to_keep:], random_to_keep)
            combined = {x[1] for x in (good_guesses + randoms)}
            first, second = combined.pop(), combined.pop()
            children_to_get = min(4, len(self._child_generation))
            all_children = {self._get_child(first, second)
                            for _ in range(children_to_get)}
            while (len(all_children) < len(self._child_generation)
                   and len(combined) > 1):
                guess1, guess2 = combined.pop(), combined.pop()
                children = [self._get_child(guess1, guess2)
                            for _ in range(4)]

                needed = len(self._child_generation) - len(all_children)
                if (len(children) > needed):
                    children = sample(children, needed)
                all_children.update(children)

            if combined:
                (second,) = combined

            while len(all_children) < len(self._child_generation):
                child = self._get_child(first, second)
                all_children.add(child)

            self._parent_generation = self._child_generation
            self._child_generation = all_children
            previous_scores = new_scores

    def _generate_first_generation(self, estimated_length: float):
        sample_size = int(5 * (estimated_length)**.5) + 1
        lengths = [self._get_random_length(estimated_length)
                   for _ in range(sample_size)]
        self._child_generation = {PasswordChecker.create_password(length)
                                  for length in lengths}
        self._parent_generation = set()
        while len(self._child_generation) < sample_size:
            # Duplicate passwords created.
            new_length = self._get_random_length(estimated_length)
            self._child_generation.add(
                PasswordChecker.create_password(new_length))

    # Raises SolvedException if the password has been cracked.
    def _get_score(self, guess: str, checker: PasswordChecker):
        correct_count, correct = checker.check_guess(guess)
        if correct:
            # Want to terminate early.
            raise SolvedException(guess)
        count_score = (correct_count+1)/(MAX_PASSWORD_LENGTH+1)

        assert len(guess) <= MAX_PASSWORD_LENGTH
        length_negative = len(guess)/((MAX_PASSWORD_LENGTH + 1)**2)
        result = count_score - length_negative
        assert 0 <= result < 1, (guess, result)
        return result

    def _get_child(self, guess1: str, guess2: str) -> str:
        length1 = len(guess1)
        length2 = len(guess2)

        min_length = min(length1, length2)
        length = randint(min_length, max(length1, length2))

        def get_next_char():
            for i in range(min_length):
                if random() < 0.5:
                    yield guess1[i]
                else:
                    yield guess2[i]

            if min_length == length:
                return

            guess1_longer = length1 > length2
            for i in range(min_length, length):
                if guess1_longer:
                    yield guess1[i]
                else:
                    yield guess2[i]

        return self._mutate("".join(get_next_char()))

    def _get_random_length(self, estimated_length):
        return randint(MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH)

    def _mutate(self, guess: str) -> str:
        length = len(guess)
        new_length = length + randint(-self._length_shift//2,
                                      self._length_shift)
        if new_length < MIN_PASSWORD_LENGTH:
            new_length = MIN_PASSWORD_LENGTH
        elif new_length > MAX_PASSWORD_LENGTH:
            new_length = MAX_PASSWORD_LENGTH

        def get_next_char():
            for i in range(new_length):
                try:
                    yield self._mutate_character(guess[i])
                except IndexError:
                    yield get_random_letter()

        return "".join(get_next_char())

    def _mutate_character(self, character: str) -> str:
        if random() < self._mutation_rate:
            return get_random_letter()
        return character


def main():
    solver = GeneticSolver()
    checker = PasswordChecker()

    for _ in range(10):
        print(checker._password)
        sleep(2)
        print(solver.solve(checker), checker.attempts, checker._password)
        checker.reset()


if __name__ == "__main__":
    main()
