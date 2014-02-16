# -*- coding: UTF-8 -*-


class History:
    def __init__(self, length):
        '''just a pseudo log class for see the history'''
        # the position in the log
        self.__cursor = 0
        # the number of line to show
        self.__length = length
        # the text
        self.__log = []

    def add_log(self, text):
        ''' Add the input in the log update the cursor also'''
        self.__log = self.__log + text
        # update the cursor (don't care if it's negative..)
        self.__set_cursor(len(self.__log) - self.__length)
        return self.__log

    def get_log(self):
        ''' return n lines from the log'''
        return self.__log[self.__cursor:self.__cursor + self.__length]

    def __set_cursor(self, cursor):
        ''' set/verify the cursor we don't want to see the -1 entry or the 213
        line of a 200 entry'''
        cursor = max(cursor, 0)  # no negative number
        cursor = min(cursor, (len(self.__log) - self.__length))
        self.__cursor = cursor
        return self.__cursor

    def increase_cursor(self):
        '''Go forward'''
        self.__set_cursor(self.__cursor + 1)

    def decrease_cursor(self):
        '''Go back'''
        self.__set_cursor(self.__cursor - 1)

    def go_to_the_top(self):
        '''Go at the beginning not used now'''
        self.__set_cursor(0)

