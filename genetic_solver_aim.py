# -*- coding: utf-8 -*-
"""
Created on Fri May 25 19:42:38 2018
"""

__author__ = "Andrew I McClement"

import itertools
from random import random, randint, sample

from evaluator import PasswordChecker
from evaluator import get_random_letter
from evaluator import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH


class SolvedException(Exception):
    def __init__(self, solution):
        self.solution = solution


class PartiallySolvedException(Exception):
    def __init__(self, partial_solution, score):
        self.partial_solution = partial_solution
        self.score = score


# TODO: Make use of case where all letters are correct but the guess is
# not yet correct (i.e. it becomes a simplified version.)
class GeneticSolver:

    def __init__(self,
                 mutation_rate: float=0.01,
                 length_shift: int=1,
                 survival_rate: float=0.01,
                 random_survival_rate: float=0.2):
        self._parent_generation = set()
        self._child_generation = set()

        self._mutation_rate = mutation_rate
        self._length_shift = length_shift
        self._survival_rate = survival_rate
        self._random_rate = random_survival_rate
        assert 0 < self._mutation_rate < 1
        assert self._length_shift > 0
        assert 0 < self._survival_rate < 1
        assert 0 < self._random_rate < 1 - self._survival_rate

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

        base = ""
        previous_scores = []

        best_result = None

        for index in itertools.count():
            try:
                new_scores = [(self._get_score(guess, checker, base), guess)
                              for guess in self._child_generation]
            except SolvedException as e:
                return e.solution
            except PartiallySolvedException as e:
                base += e.partial_solution
                assert checker._password.startswith(base)
                print(f"New base is {base}")
                self._child_generation = {x[len(base):]
                                          for x in self._child_generation}
                best_result = (e.score, "")
                previous_scores = [(x[0], x[1][len(e.partial_solution):])
                                   for x in previous_scores]
                continue

            scores = new_scores + previous_scores
            if best_result:
                scores.append(best_result)
            scores.sort(reverse=True)

            best_result = scores[0]
            if index % 100 == 0:
                print("hi", best_result, "index", index, "base", base)

            good_guesses = scores[:good_to_keep]
            assert random_to_keep < len(scores) - good_to_keep
            randoms = sample(scores[good_to_keep:], random_to_keep)
            combined = {x[1] for x in (good_guesses + randoms)}
            first, second = combined.pop(), combined.pop()
            children_to_get = min(4, len(self._child_generation))

            min_length = max(0, MIN_PASSWORD_LENGTH-len(base))
            max_length = MAX_PASSWORD_LENGTH - len(base)
            all_children = set(self._breed(first, second, min_length,
                                           max_length))

            if len(all_children) > children_to_get:
                all_children = set(sample(all_children, children_to_get))

            while (len(all_children) < len(self._child_generation)
                   and len(combined) > 1):
                guess1, guess2 = combined.pop(), combined.pop()
                children = set(self._breed(guess1, guess2, min_length,
                                           max_length))

                needed = len(self._child_generation) - len(all_children)
                if (len(children) > needed):
                    children = sample(children, needed)
                all_children.update(children)

            if combined and len(all_children) < len(self._child_generation):
                (second,) = combined

            while len(all_children) < len(self._child_generation):
                child = self._get_child(first, second,
                                        max(0, MIN_PASSWORD_LENGTH-len(base)),
                                        MAX_PASSWORD_LENGTH - len(base))
                all_children.add(child)

            self._parent_generation = self._child_generation
            self._child_generation = all_children
            previous_scores = new_scores

    def _generate_first_generation(self, estimated_length: float):
        sample_size = int(50 * estimated_length) + 2
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
    def _get_score(self, guess: str, checker: PasswordChecker, base: str):
        correct_count, correct = checker.check_guess(base + guess)
        if correct:
            # Want to terminate early.
            raise SolvedException(base + guess)

        count_score = (correct_count+1)/(MAX_PASSWORD_LENGTH+1)

        if correct_count == len(guess + base) != len(base):
            raise PartiallySolvedException(guess, count_score)

        assert len(guess) <= MAX_PASSWORD_LENGTH - len(base)
        length_negative = len(guess)/((MAX_PASSWORD_LENGTH + 1)**2)
        result = count_score - length_negative
        assert 0 <= result < 1, (guess, result)
        return result

    def _breed(self, guess1, guess2, min_length, max_length):
        yield self._get_child(guess1, guess2, min_length, max_length)
        yield self._get_child(guess1, guess2, min_length, max_length)
        yield self._get_child(guess1, guess2, min_length, max_length)
        yield self._get_child(guess1, guess2, min_length, max_length)
        yield self._get_child(guess1, guess2, min_length, max_length)
        yield self._get_child(guess1, guess2, min_length, max_length)
        yield self._mutate(guess1, min_length, max_length)
        yield self._mutate(guess2, min_length, max_length)

    def _get_child(self,
                   guess1: str,
                   guess2: str,
                   min_length2,
                   max_length2) -> str:
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

        return self._mutate("".join(get_next_char()), min_length2, max_length2)

    def _get_random_length(self, estimated_length):
        return randint(MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH)

    def _mutate(self, guess: str, min_length: int, max_length: int) -> str:
        length = len(guess)
        new_length = length + randint(-self._length_shift,
                                      self._length_shift)
        if new_length < min_length:
            new_length = min_length
        elif new_length > max_length:
            new_length = max_length

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

    solutions = []
    for _ in range(10):
        solutions.append((solver.solve(checker), checker.attempts,
                          checker._password))
        checker.reset()
        print("Solved one!")

    print(solutions)


if __name__ == "__main__":
    main()
