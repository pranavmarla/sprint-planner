__author__ = 'Pranav Marla'


# This generator function returns a generator iterator. Every time the generator iterator is iterated upon, it returns the next consecutive number.
def consecutive_number_generator_function():

    number = 1
    
    while True:
        yield number
        number += 1


class Sprint:

    def __init__(self, id, end_date, name=None):
        self.id = id
        self.name = name
        self.end_date = end_date


class Story:

    def __init__(self):

        self.id = ''
        self.name = ''

        # Size (i.e. story points) and priority accept all non-negative values, including 0 and fractions.
        self.size = 0
        self.priority = 0

        # If story B depends on story A, A is a parent of B, and B is a child of A.
        self.parents = []
        self.has_children = False

        # When displaying the results at the end, the user might want the stories to display additional fields (eg. epic).
        self.additional_fields = None


        # Each element of the 'parents' list is a story ID.
        if parents is None:
        
        self.has_children = has_children

        # When displaying the results at the end, the user might want the stories to display additional fields (eg. epic).
        # Those fields are stored as a dict.
        if additional_fields is None:

    def __repr__(self):