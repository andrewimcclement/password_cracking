# -*- coding: utf-8 -*-
"""
Created on Thu May 24 20:17:44 2018
"""

__author__ = "Andrew I McClement"

from random import randint


def get_random_letter():
    return chr(97 + randint(0, 25))


class PasswordChecker:
    def __init__(self):
        self._length = randint(5, 100)
        self._password = "".join((get_random_letter()
                                 for i in range(self._length)))

    def check_guess(self, guess) -> (int, bool):
        successes = sum((x[0] == x[1] for x in zip(self._password, guess)))
        return successes, guess == self._password


if __name__ == "__main__":
    pass
