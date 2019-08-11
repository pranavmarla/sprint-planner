__author__ = 'Pranav Marla'


# This generator function returns a generator iterator. Every time the generator iterator is iterated upon, it returns the next consecutive number.
def consecutive_number_generator_function():

    number = 1
    
    while True:
        yield number
        number += 1


class Sprint:

    SPRINT_ID_GENERATOR = consecutive_number_generator_function()

    def __init__(self, end_date, total_capacity, name=None):
        
        self.id = next(self.SPRINT_ID_GENERATOR)
        self.name = name
        self.end_date = end_date
        
        # Measured in story points
        # Accepts all non-negative values, including 0 and floating point numbers.
        self.total_capacity = total_capacity
        self.available_capacity = self.total_capacity
        
        self.stories = []

    def __repr__(self):
        return 'Sprint(id={}, name={}, end_date={}, total_capacity={}, available_capacity={}, stories={})'.format(self.id, self.name, self.end_date, self.total_capacity, self.available_capacity, self.stories)


class Story:

    def __init__(self, id, name=None, size=1, priority=0, parents=None, has_children=False, additional_fields=None):

        self.id = id
        self.name = name

        # Size accepts all non-negative values, including 0 and floating point numbers.
        self.size = size
        # Priority accepts all values, including negatie numbers, 0 and floating point numbers.
        self.priority = priority

        # If story B depends on story A, A is a parent of B, and B is a child of A.

        # Each element of the 'parents' list is a story ID.
        if parents is None:
            parents = []
        self.parents = parents
        
        self.has_children = has_children

        # When displaying the results at the end, the user might want the stories to display additional fields (eg. epic).
        # Those fields are stored as a dict.
        if additional_fields is None:
            additional_fields = {}
        self.additional_fields = additional_fields

    def __repr__(self):
        return 'Story(id={}, name={}, size={}, priority={}, parents={}, has_children={}, additional_fields={})'.format(self.id, self.name, self.size, self.priority, self.parents, self.has_children, self.additional_fields)