__author__ = 'Pranav Marla'


import argparse
from datetime import date, datetime
import json
from operator import attrgetter


# NOTE: date.resolution is the smallest possible difference between non-equal date objects (i.e. 1 day).
ONE_DAY = date.resolution

# Min possible date (Jan 01, 0001)
MIN_DATE = date.min

# Max possible date (Dec 31, 9999)
MAX_DATE = date.max

# We can convert a string representation of a date to the corresponding date object as long as the string adheres to this format.
# This format can be thought of as 'YYYY-MM-DD'
# Eg. '2019-08-23'
DATE_STRING_FORMAT = '%Y-%m-%d'


# This generator function returns a generator iterator. Every time the generator iterator is iterated upon, it returns the next consecutive number.
def consecutive_number_generator_function():

    number = 1
    
    while True:
        yield number
        number += 1


class Sprint:

    SPRINT_ID_GENERATOR = consecutive_number_generator_function()

    def __init__(self, start_date, end_date, total_capacity, name=None):
        
        self.id = next(self.SPRINT_ID_GENERATOR)
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        
        # Measured in story points
        # Accepts all non-negative values, including 0 and floating point numbers.
        self.total_capacity = total_capacity
        self.available_capacity = self.total_capacity
        
        self.stories = []

    def __repr__(self):
        return 'Sprint(id={}, name={}, start_date={}, end_date={}, total_capacity={}, available_capacity={}, stories={})'.format(self.id, self.name, self.start_date, self.end_date, self.total_capacity, self.available_capacity, self.stories)


class Story:

    def __init__(self, id, name=None, size=1, priority=0, start_date=MIN_DATE, end_date=MAX_DATE, children_ids=None):

        self.id = id
        self.name = name

        # Size accepts all non-negative values, including 0 and floating point numbers.
        self.size = size
        
        # Priority accepts all values, including negative numbers, 0 and floating point numbers.
        self.priority = priority

        self.start_date = start_date
        self.end_date = end_date

        # If story B depends on story A, A is a parent of B, and B is a child of A.
        
        if children_ids is None:
            children_ids = []
        # For consistency, so that we can easily tell when two stories share the same group of children, sort their IDs.
        children_ids.sort()

        # Each element of the 'self.children_ids' list is a story ID (i.e. a string).
        self.children_ids = children_ids
        
        # Each element of the 'self.children' list will be an actual story whose ID is the corresponding element in the 'self.children_ids' list.
        # We will populate this list later.
        self.children = []

        # For a story to be normalized:
        # a) Its priority needs to be >= max(its children's priorities)
        # b) Its end_date needs to be <= (min(its children's end dates) - 1 day)
        #
        # If the story has no children, then it is already normalized by default.
        if not self.children_ids:
            self.is_normalized = True
        else:
            self.is_normalized = False

    def __repr__(self):
        return 'Story(id={}, name={}, size={}, priority={}, start_date={}, end_date={}, children_ids={}, children={}, is_normalized={})'.format(self.id, self.name, self.size, self.priority, self.start_date, self.end_date, self.children_ids, self.children, self.is_normalized)


def parse_command_line_args():

    # Note: If any of the arguments are not supplied, their value with either be None or whatever alternate default value we specify below.
    # To make it easy to clean up the arguments, ensure their default values are valid strings.
    arg_parser = argparse.ArgumentParser(argument_default='')
    
    # For ease of maintenance, make all arguments optional
    arg_parser.add_argument('--input')

    args = arg_parser.parse_args()

    # For safety, remove any extraneous whitespace
    return \
        (
            args.input.strip()
        )

# input_file_path is a string containing the file path of the input file
def load_input_data(input_file_path):

    # No input file path argument was provided, or a blank string was provided
    if not input_file_path:
        raise ValueError('No input file path provided!')

    with open(input_file_path) as input_file:
        input_dict = json.load(input_file)
    
    sprints = load_sprint_data(input_dict)
    stories, id_to_story_dict = load_story_data(input_dict)

    return (sprints, stories, id_to_story_dict)


def load_sprint_data(input_dict):

    sprints = []
    sprint_dicts_list = input_dict['sprints']

    for sprint_dict in sprint_dicts_list:

        # Dictionary containing the arguments to be provided when creating a new Sprint object.
        # Initialize it with the mandatory arguments.
        sprint_constructor_args_dict = \
            {
                'start_date': convert_str_to_date(sprint_dict['start_date']), 
                'end_date': convert_str_to_date(sprint_dict['end_date']), 'total_capacity': sprint_dict['capacity']
            }

        # If the optional arguments are present, add them as well
        if 'name' in sprint_dict:
            sprint_constructor_args_dict['name'] = sprint_dict['name']

        # Now that we've assembled all the arguments, use them to create a new Sprint object and add it to the list of Sprint objects
        sprints.append(Sprint(**sprint_constructor_args_dict))
    
    # To be safe, sort sprints by their end date (in ascending order)
    sprints.sort(key=attrgetter('end_date'))

    return sprints


# Given a string representation of a date, return the corresponding date object
def convert_str_to_date(date_string, date_string_format=DATE_STRING_FORMAT):
    # Eg. Given a date string of '2019-08-23', and a date string format of '%Y-%m-%d', this function will return the corresponding date object: datetime.date(2019, 8, 23).
    return(datetime.strptime(date_string, date_string_format).date())


def load_story_data(input_dict, default_end_date=MAX_DATE):

    stories = []
    story_dicts_list = input_dict['stories']

    # Dictionary mapping story ID (a string) to the corresponding Story object
    id_to_story_dict = {}

    for story_dict in story_dicts_list:

        # Dictionary containing the arguments to be provided when creating a new Story object.
        # Initialize it with the mandatory arguments.
        story_constructor_args_dict = {'id': story_dict['id']}

        # If the optional arguments are present, add them as well

        if 'name' in story_dict:
            story_constructor_args_dict['name'] = story_dict['name']
        
        if 'size' in story_dict:
            story_constructor_args_dict['size'] = story_dict['size']
        
        if 'priority' in story_dict:
            story_constructor_args_dict['priority'] = story_dict['priority']
        
        if 'start_date' in story_dict:
            story_constructor_args_dict['start_date'] = convert_str_to_date(story_dict['start_date'])

        if 'end_date' in story_dict:
            story_constructor_args_dict['end_date'] = convert_str_to_date(story_dict['end_date'])
        
        if 'prerequisite_for' in story_dict:
            story_constructor_args_dict['children_ids'] = story_dict['prerequisite_for']

        # Now that we've assembled all the arguments, use them to create a new Story object and add it to the list of Story objects
        story = Story(**story_constructor_args_dict)
        stories.append(story)
        id_to_story_dict[story.id] = story

    return stories, id_to_story_dict


# At this point, each story has a list of the (string) IDs of its children, but its list of the actual children themselves is empty -- populate the latter list with the children whose IDs are the corresponding elements in the former list.
def populate_children_from_ids(stories, id_to_story_dict):
    for story in stories:
        for child_id in story.children_ids:
            story.children.append(id_to_story_dict[child_id])


# If stories B and C both depend on A then, for consistency, we need to ensure that:
# a) A's priority is >= max(B and C's priorities)
# b) A's end_date is <= (min(B and C's end dates) - 1 day)
#    NOTE: We make sure that A's end_date is at least 1 day before the earliest end_date of all the stories that depend on A to ensure that A is slotted out before the stories that depend on A (note that they can still end up in the same sprint together, but B/C should never end up in an EARLIER sprint than A)!
#
# If a story's priority and end_date adhere to the above rules regarding the corresponding values of its children, then we say that that story is 'normalized'.
def normalize_stories(stories):

    # children_values_dict is a dictionary mapping a tuple of story IDs [here: ('B', 'C')] to a tuple of their max priority and min end_date.
    children_values_dict = {}
    
    # For each story, calculate the max priority and min end_date of its children and potentially change its own priority and end_date based on those values (i.e. normalize the story).
    for story in stories:
        normalize_story(story, children_values_dict)
    
    #! DEBUG
    # print('\nchildren_values_dict:\n{}\n'.format(children_values_dict))


# NOTE: This can potentially take exponential running time if every parent has a unique set of children but we assume that, in practice, this situation will never arise.
# Recursive helper function for normalize_stories()
def normalize_story(story, children_values_dict, one_day=ONE_DAY):

    # If the story is already normalized, there's nothing to do
    if story.is_normalized:
        return

    # Note: When the story was created, if it had no children, we made sure to mark it as normalized right then -- so, at this point, if the story is not already normalized, we know it has children.
    children = story.children

    # Sort its list of children by their IDs, to ensure consistency if multiple parents query this same group of children.
    children.sort(key=attrgetter('id'))

    # See if the max priority and min end_date have already been calculated for this particular group of children.

    # If they have, then they will already be present in children_values_dict with a key formed from the IDs of the sorted list of children.
    key = tuple([child.id for child in children])
    if key in children_values_dict:
        max_priority, min_end_date = children_values_dict[key]
    
    # The max priority and min end_date have not already been calculated for this particular group of children.
    else:

        # First ensure each child is normalized
        for child in children:
            normalize_story(child, children_values_dict)
        
        # Then, using normalized priority and end_date values of all the children, calculate the max priority and min end_date for this group of children.
        max_priority = max([child.priority for child in children])
        min_end_date = min([child.end_date for child in children])

        # Now that we've calculated the max priority and min end_date for this group of children, save those values to save us time with any future parents of this same group of children.
        children_values_dict[key] = (max_priority, min_end_date)

    if story.priority < max_priority:
        story.priority = max_priority
    
    if story.end_date > (min_end_date - one_day):
        story.end_date = min_end_date - one_day

    # This story is now normalized
    story.is_normalized = True

    return


# Sort stories using the following algorithm:
# Given two stories A and B:
# If A has a higher priority than B, then A is sorted ahead of B.
# If their priorities are the same, but A has an earlier end_date than B, then A is sorted ahead of B.
# If their priorities and end dates are the same, but A is bigger than B, then A is sorted ahead of B.
def sort_stories(stories):

    # To get the resulting order we want, we need to sort by the LEAST important attribute first!

    # Sort stories by size in descending order
    stories.sort(key=attrgetter('size'), reverse=True)

    # Sort resulting stories by end_date in ascending order
    stories.sort(key=attrgetter('end_date'))
    
    # Sort resulting stories by priority in descending order
    stories.sort(key=attrgetter('priority'), reverse=True)


#! DEBUG: Test this with a sprint that can take in a story, but the story's end_date is already passed -- should not be slotted in!

# Slot stories into sprints, following the order of the 'stories' list (if story A appears before story B in the 'stories' list, then A will be slotted into a sprint before B) and the 'sprints' list (if sprint 1 appears before sprint 2 in the 'sprints' list, then we will attempt to slot stories into sprint 1 before sprint 2)
# Note that, depending on how much space is left in each sprint, even though we try to slot story A into one of the sprints before trying to slot story B, if B is smaller than A, B might end up in an earlier sprint than A (i.e. if that sprint didn't have enough space for A, forcing A to go to the next sprint, but had enough space for B).
def slot_stories(stories, sprints):

    # The 'stories' and 'sprints' lists might be used even after this function is done -- thus, do NOT directly modify them!

    # Contains stories that we have not yet attempted to slot
    available_stories = stories.copy()

    # Contains sprints that have available capacity
    available_sprints = sprints.copy()

    # Contains sprints that have no available capacity left.
    full_sprints = []

    # Contains all the stories that we were not able to slot into any sprints
    remaining_stories = []

    # Since we will be modifying available_stories in this 'for' loop, do NOT iterate over available_stories itself!
    for story in stories:

        story_size = story.size

        # Try to slot the story into the first sprint that has enough space for it, and that abides by its start and end date constraints
        for sprint in available_sprints:

            if (sprint.available_capacity >= story_size) and (sprint.end_date >= story.start_date) and (sprint.start_date <= story.end_date):
                sprint.stories.append(story)
                sprint.available_capacity -= story_size
                available_stories.remove(story)
                break
            
            elif sprint.available_capacity == 0:
                full_sprints.append(sprint)
        
        # If we know any of the sprints are full, remove it from the 'available_sprints' list so that we don't waste time trying to slot the next story into it
        for full_sprint in full_sprints:
            available_sprints.remove(full_sprint)
        
        # Now that we've removed all the full sprints from 'available_sprints', reset 'full_sprints'
        if full_sprints:
            full_sprints.clear()

        # If all the sprints are full, don't bother trying to slot the remaining stories
        if not available_sprints:
            remaining_stories = available_stories
            break

    # Enter this 'else' clause if we did NOT exit the above 'for' loop by breaking out of it.
    else:

        # It is possible to have stories remaining (unslotted) without having already placed them in remaining_stories:
        # a) If there is not enough space in the remaining sprints to slot in the remaining stories, but the remaining sprints are NOT full!
        # b) If the last sprint was perfectly filled when the final story in the 'stories' list was slotted in -- note that there are still other unslotted stories in the 'stories' list, but there wasn't enough space to slot them in, so they were skipped over before we got to this final story.
        if available_stories:
            remaining_stories = available_stories
    
    return remaining_stories