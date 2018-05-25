# -*- coding: utf-8 -*-
"""
Created on Fri May 25 19:42:38 2018
"""

__author__ = "Andrew I McClement"

from evaluator import PasswordChecker
from evaluator import get_random_letter
from evaluator import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH
from random import random, randint
from math import log


class GeneticSolver:

    def __init__(self, mutation_rate: float=0.1, length_shift: int=3):
        self._parent_generation = []
        self._child_generation = []

        self._mutation_rate = mutation_rate
        self._length_shift = length_shift

    def solve(self, checker: PasswordChecker) -> str:
        #self._par
        pass

    def _generate_first_generation(self, estimated_length: int):
        sample_size = int(2 * log(estimated_length)) + 7
        lengths = [self._get_random_length(estimated_length)
                   for _ in range(sample_size)]
        self._parent_generation = [PasswordChecker.create_password(length)
                                   for length in lengths]
        self._child_generation = []

    def _get_random_length(self, estimated_length):
        return randint(MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH)

    def _mutate(self, guess: str) -> str:
        length = len(guess)
        new_length = length + randint(-self._length_shift, self._length_shift)
        if new_length < 5:
            new_length = 5
        elif new_length > 100:
            new_length = 100

        def get_next_char():
            for i in range(new_length):
                if i > length:
                    yield get_random_letter()
                else:
                    yield self._mutate_character(guess[i])

        return "".join(get_next_char())

    @classmethod
    def _mutate_character(cls, character: str) -> str:
        if random() < cls._mutation_rate:
            return get_random_letter()
        return character


def main():
    solver = GeneticSolver()
    checker = PasswordChecker()

    for _ in range(10):
        print(solver.solve(checker), checker.attempts, checker._password)
        checker.reset()


if __name__ == "__main__":
    main()
