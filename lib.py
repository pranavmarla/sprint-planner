__author__ = 'Pranav Marla'

from operator import attrgetter

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

    def __init__(self, id, name=None, size=1, priority=0, deadline=None, parents=None, has_children=False, additional_fields=None):

        self.id = id
        self.name = name

        # Size accepts all non-negative values, including 0 and floating point numbers.
        self.size = size
        # Priority accepts all values, including negatie numbers, 0 and floating point numbers.
        self.priority = priority

        self.deadline = deadline

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
        return 'Story(id={}, name={}, size={}, priority={}, deadline={}, parents={}, has_children={}, additional_fields={})'.format(self.id, self.name, self.size, self.priority, self.deadline, self.parents, self.has_children, self.additional_fields)

# Sort stories using the following algorithm:
# Given two stories A and B:
# If A has a higher priority than B, then A is sorted ahead of B.
# If their priorities are the same, but A has an earlier deadline than B, then A is sorted ahead of B.
# If their priorities and deadlines are the same, but A is bigger than B, then A is sorted ahead of B.
def sort_stories(stories):

    # To get the resulting order we want, we need to sort by the LEAST important attribute first!

    # Sort stories by size in descending order
    stories.sort(key=attrgetter('size'), reverse=True)

    # Sort resulting stories by deadline in ascending order
    stories.sort(key=attrgetter('deadline'))
    
    # Sort resulting stories by priority in descending order
    stories.sort(key=attrgetter('priority'), reverse=True)

