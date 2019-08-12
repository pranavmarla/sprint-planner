__author__ = 'Pranav Marla'


from datetime import date
from operator import attrgetter


# NOTE: date.resolution is the smallest possible difference between non-equal date objects (i.e. 1 day).
ONE_DAY = date.resolution


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


# If stories B and C both depend on A then, for consistency, we need to ensure that:
# a) A's priority is >= max(B and C's priorities)
# b) A's deadline is <= (min(B and C's deadlines) - 1 day)
#    NOTE: We make sure that A's deadline is at least 1 day before the earliest deadline of all the stories that depend on A to ensure that A is slotted out before the stories that depend on A (note that they can still end up in the same sprint together, but B/C should never end up in an EARLIER sprint than A)!
#
# If a story's priority and deadline adhere to the above rules regarding the corresponding values of its children, then we say that that story is 'normalized'.
def normalize_stories(stories):

    # dependent_values_dict is a dictionary mapping a tuple of story IDs [here: ('B', 'C')] to a tuple of their max priority and min deadline.
    # The stories B and C depend on another story A (i.e. they are dependents of A).
    dependent_values_dict = {}
    
    # For each story, calculate the max priority and min deadline of its children and potentially change its own priority and deadline based on those values (i.e. normalize the story).
    for story in stories:
        normalize_story(story, dependent_values_dict)

#! DEBUG:
#! a) Need to test this
#! b) This can still potentially take exponential running time if every parent has a unique set of children.
# Recursive helper function for normalize_stories()
def normalize_story(story, dependent_values_dict, one_day=ONE_DAY):

    # If the story is already normalized, there's nothing to do
    if story.is_normalized:
        return

    # Note: When the story was created, if it had no children, we made sure to mark it as normalized right then -- so, at this point, if the story is not already normalized, we know it has children.
    children = story.children

    # Sort its list of children by their IDs, to ensure consistency when multiple parents query this same group of children.
    children.sort(key=attrgetter('id'))

    # See if the max priority and min deadline have already been calculated for this particular group of children.

    # If they have, then they will be stored in dependent_values_dict with a key formed from the IDs of the sorted list of children.
    key = tuple([child.id for child in children])
    if key in dependent_values_dict:
        max_priority, min_deadline = dependent_values_dict[key]
    
    # The max priority and min deadline have not already been calculated for this particular group of children.
    else:

        # First ensure each child is normalized
        for child in children:
            normalize_story(child, dependent_values_dict)
        
        # Then, using normalized priority and deadline values of all the children, calculate the max priority and min deadline for this group of children.
        max_priority = max([child.priority for child in children])
        min_deadline = min([child.deadline for child in children])

        # Now that we've calculated the max priority and min deadline for this group of children, save those values to save us time with any future parents of this same group of children.
        dependent_values_dict[key] = (max_priority, min_deadline)

    if story.priority < max_priority:
        story.priority = max_priority
    
    if story.deadline > (min_deadline - one_day):
        story.deadline = min_deadline - one_day

    # This story is now normalized
    story.is_normalized = True

    return


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