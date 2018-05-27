# -*- coding: utf-8 -*-
"""
Created on Thu May 24 20:17:44 2018
"""

__author__ = "Andrew I McClement"

from random import randint

CHARACTERS_PERMITTED = 26
MIN_PASSWORD_LENGTH = 5
MAX_PASSWORD_LENGTH = 100


def get_random_letter():
    return get_letter_from_integer(randint(0, CHARACTERS_PERMITTED - 1))


def get_letter_from_integer(integer: int) -> str:
    return chr(97 + integer)


class PasswordChecker:
    def __init__(self):
        self.reset()
        self.regenerate()

    def check_guess(self, guess) -> (int, bool):
        successes = sum((x[0] == x[1] for x in zip(self._password, guess)))
        self._attempts += 1
        return successes, guess == self._password

    @property
    def attempts(self):
        return self._attempts

    @staticmethod
    def create_password(length):
        return "".join((get_random_letter() for i in range(length)))

    def reset(self):
        self._attempts = 0

    def regenerate(self):
        self._length = randint(MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH)
        self._password = self.create_password(self._length)


if __name__ == "__main__":
    pass
