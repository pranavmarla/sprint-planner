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

    def __init__(self, id, name=None, size=1, priority=0, deadline=None, children=None, additional_fields=None):

        self.id = id
        self.name = name

        # Size accepts all non-negative values, including 0 and floating point numbers.
        self.size = size
        # Priority accepts all values, including negative numbers, 0 and floating point numbers.
        self.priority = priority

        self.deadline = deadline

        # If story B depends on story A, A is a parent of B, and B is a child of A.

        #! DEBUG:
        #! Below, we say that parents and children are list of stories (not just story IDs), but customer will only be supplying us with story IDs!!
        # Each element of the 'self.children' list is a story.
        if children is None:
            children = []
        self.children = children

        # For a story to be normalized:
        # a) Its priority needs to be >= max(its children's priorities)
        # b) Its deadline needs to be <= (min(its children's deadlines) - 1 day)
        #
        # If the story has no children, then it is already normalized by default.
        if not self.children:
            self.is_normalized = True
        else:
            self.is_normalized = False

        # When displaying the results at the end, the user might want the stories to display additional fields (eg. epic).
        # Those fields are stored as a dict.
        if additional_fields is None:
            additional_fields = {}
        self.additional_fields = additional_fields

    def __repr__(self):
        return 'Story(id={}, name={}, size={}, priority={}, deadline={}, children={}, is_normalized = {}, additional_fields={})'.format(self.id, self.name, self.size, self.priority, self.deadline, self.children, self.is_normalized, self.additional_fields)

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


# Slot stories into sprints, following the order of the 'stories' list (if story A appears before story B in the 'stories' list, then A will be slotted into a sprint before B) and the 'sprints' list (if sprint 1 appears before sprint 2 in the 'sprints' list, then we will attempt to slot stories into sprint 1 before sprint 2)
# Note that, depending on how much space is left in each sprint, even though we try to slot story A into one of the sprints before trying to slot story B, if B is smaller than A, B might end up in an earlier sprint than A (i.e. if that sprint didn't have enough space for A, forcing A to go to the next sprint, but had enough space for B).
def slot_stories(stories, sprints):

    # Contains sprints that have available capacity
    available_sprints = sprints.copy()

    # Contains sprints that have no available capacity.
    full_sprints = []

    # Contains all the stories that could not be slotted into any sprints
    overflow_stories = []

    for story in stories.copy():

        story_size = story.size

        # Try to slot the story into the first sprint that has enough space for it
        for sprint in available_sprints:

            if sprint.available_capacity >= story_size:
                sprint.stories.append(story)
                sprint.available_capacity -= story_size
                stories.remove(story)
                break
            
            elif sprint.available_capacity == 0:
                full_sprints.append(sprint)
        
        # If we know any of the sprints are full, remove it from the 'sprints' list so that we don't waste time trying to slot the next story into it
        for full_sprint in full_sprints:
            available_sprints.remove(full_sprint)
        
        # If all the sprints are full, don't bother trying to slot the remaining stories
        if not available_sprints:
            overflow_stories = stories
            break

        # Now that we've removed all the full sprints from 'sprints', reset 'full_sprints'
        if full_sprints:
            full_sprints.clear()
    
    # Enter this 'else' clause if we did NOT exit the above 'for' loop by breaking out of it.
    else:

        # It is possible to have stories remaining (unslotted) without having already placed them in overflow_stories:
        # a) If there is not enough space in the remaining sprints to slot in the remaining stories, but the remaining sprints are NOT full!
        # b) If the last sprint was perfectly filled when the last story in the 'stories' list was slotted in -- note that there are still other unslotted stories in the 'stories' list, but there wasn't enough space to slot them in, so they were skipped over before we got to this last story.
        if stories:
            overflow_stories = stories
    
    return overflow_stories