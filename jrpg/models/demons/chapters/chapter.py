# -*- coding: UTF-8 -*-


# Abstract Class for load the file
class DemonBookChapter:
    pass

    def __init__(self, filename):
        '''Open the file. read each line
        '''
        self.filename = filename
        f = open(filename)
        lines = f.readlines()
        f.close()
        self.demons = []
        for line in lines:
            self.demons.append(self.get_one_monster(line))

    def get_title_of_the_chapter(self):
        ''' return the name of chapter'''
        return self.name

    def get_the_list_of_demon(self):
        ''' return the list'''
        return self.demons

    def get_one_monster(self):
        '''this methods is call for each line of the file'''
        pass
