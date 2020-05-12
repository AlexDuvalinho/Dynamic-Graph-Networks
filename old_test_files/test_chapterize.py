from src.third_party.chapterize import Book

"""
Use to test chapterize
if this work it will create a new folder containing all the chapter from 1984
"""
if __name__ == '__main__':
    book = Book(filename='../data/raw_text/hp1.txt', nochapters=False, stats=False)
