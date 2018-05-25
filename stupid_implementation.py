# -*- coding: utf-8 -*-
"""
Created on Thu May 24 20:25:44 2018
"""

__author__ = "Andrew I McClement"

from time import sleep
from evaluator import get_letter_from_integer, PasswordChecker
from evaluator import get_random_letter
from evaluator import MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH
from random import randint


class StupidSolver:
    def __init__(self, checker: PasswordChecker):
        self.checker = checker
        self.guess = None

    def solve(self) -> int:
        self.guess = "0"*5
        correct_count = 0
        correct = False
        for i in range(100):
            correct_count, correct = self.checker.check_guess(self.guess)
            if correct_count == len(self.guess) and not correct:
                self.guess += "0"

            if correct:
                return self.checker.attempts

            self.guess = self._improve_guess(self.guess, i, correct_count)

        raise AssertionError("Did not solve password.")

    def _improve_guess(self, guess: str, index, initial_correct) -> str:

        for i in range(26):
            guess = (guess[:index] + get_letter_from_integer(i)
                     + guess[index + 1:])
            current_correct, _ = self.checker.check_guess(guess)
            if current_correct == initial_correct + 1:
                return guess

        raise AssertionError(f"Character at index {index} is not a letter.")


class ReallyStupidSolver:
    def solve(self, checker: PasswordChecker) -> str:
        while True:
            length = randint(MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH)
            guess = "".join((get_random_letter() for _ in range(length)))
            _, success = checker.check_guess(guess)
            if success:
                return guess


if __name__ == "__main__":
    puzzles = [PasswordChecker() for _ in range(10)]
    stupid_solvers = [StupidSolver(checker) for checker in puzzles]
    stupid_solutions = [(solver.solve(), solver.guess)
                        for solver in stupid_solvers]

    print(stupid_solutions)

    for checker in puzzles:
        checker.reset()

    solver = ReallyStupidSolver()
    terrible_solutions = [(solver.solve(checker), checker.attemps)
                          for checker in puzzles]

    print(terrible_solutions)
    sleep(5)
