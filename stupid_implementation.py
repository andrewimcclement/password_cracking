# -*- coding: utf-8 -*-
"""
Created on Thu May 24 20:25:44 2018
"""

__author__ = "Andrew I McClement"

from time import sleep
from evaluator import get_letter_from_integer, PasswordChecker


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

        assert False, "Did not solve password."

    def _improve_guess(self, guess: str, index, initial_correct) -> str:

        for i in range(26):
            guess = (guess[:index] + get_letter_from_integer(i)
                     + guess[index + 1:])
            current_correct, _ = self.checker.check_guess(guess)
            if current_correct == initial_correct + 1:
                return guess

        assert False, f"Character at index {index} is not a letter."


if __name__ == "__main__":
    puzzles = [StupidSolver(PasswordChecker()) for _ in range(10)]
    print([(solver.solve(), solver.guess) for solver in puzzles])
    sleep(5)
