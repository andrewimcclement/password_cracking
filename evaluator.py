# -*- coding: utf-8 -*-
"""
Created on Thu May 24 20:17:44 2018
"""

__author__ = "Andrew I McClement"

from random import randint


def get_random_letter():
    return get_letter_from_integer(randint(0, 25))


def get_letter_from_integer(integer: int) -> str:
    return chr(97 + integer)


class PasswordChecker:
    def __init__(self, password=None):
        self._length = randint(5, 100)
        if password is None:
            self._password = self.create_password()
        else:
            self._password = password

        self._attempts = 0

    def check_guess(self, guess) -> (int, bool):
        successes = sum((x[0] == x[1] for x in zip(self._password, guess)))
        self._attempts += 1
        return successes, guess == self._password

    @property
    def attempts(self):
        return self._attempts

    def create_password(self):
        return "".join((get_random_letter() for i in range(self._length)))


if __name__ == "__main__":
    pass
