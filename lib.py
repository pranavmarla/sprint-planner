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

    def __init__(self, start_date, end_date, total_capacity, assignee_total_capacities=None, name=None):
        
        self.id = next(self.SPRINT_ID_GENERATOR)
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        
        # Measured in story points
        # Accepts all non-negative values, including 0 and floating point numbers.
        self.total_capacity = total_capacity
        self.available_capacity = self.total_capacity

        # Dictionary mapping name of assignee (person doing the work) to the max number of story points they can do in this sprint
        if assignee_total_capacities is None:
            assignee_total_capacities = {}
        self.assignee_total_capacities = assignee_total_capacities

        # Dictionary mapping name of assignee (person doing the work) to the remaining number of story points they can do in this sprint.
        # Note that although this is a shallow copy, since the values here are simple numbers (not objects like lists), it doesn't matter -- changes made to the values in one dict do not affect the corresponding values in the other dict.
        self.assignee_available_capacities = self.assignee_total_capacities.copy()
        
        self.stories = []

    def __repr__(self):
        return 'Sprint(id={}, name={}, start_date={}, end_date={}, total_capacity={}, available_capacity={}, assignee_total_capacities={}, assignee_available_capacities={}, stories={})'.format(self.id, self.name, self.start_date, self.end_date, self.total_capacity, self.available_capacity, self.assignee_total_capacities, self.assignee_available_capacities, self.stories)


class Story:

    def __init__(self, id, name=None, size=1, importance=0, start_date=MIN_DATE, end_date=MAX_DATE, assignee=None, children_ids=None):

        self.id = id
        self.name = name

        # Size accepts all non-negative values, including 0 and floating point numbers.
        if size < 0:
            raise ValueError("Story {} has a size of {}: Story sizes have to be >= 0!".format(id, size))
        self.size = size
        
        # Importance accepts all values, including negative numbers, 0 and floating point numbers.
        self.importance = importance

        self.start_date = start_date
        self.end_date = end_date

        # The name of the person who is doing this story
        self.assignee = assignee

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
        # a) Its importance value needs to be >= max(its children's importance values)
        # b) Its end_date needs to be <= (min(its children's end dates) - 1 day)
        #
        # If the story has no children, then it is already normalized by default.
        if not self.children_ids:
            self.is_normalized = True
        else:
            self.is_normalized = False
        
        # Note: Each sprint already links to their stories -- don't have the stories link back to their assigned sprint as well, since that will cause an "infinite" recursion when printing a story/sprint` (Python will automatically stop printing it after a while, but it will still be a lot of output).
        # The ID of the sprint that this story has been slotted into
        self.assigned_sprint_id = None

    def __repr__(self):
        return 'Story(id={}, name={}, size={}, importance={}, start_date={}, end_date={}, assignee={}, children_ids={}, children={}, is_normalized={}, assigned_sprint_id={})'.format(self.id, self.name, self.size, self.importance, self.start_date, self.end_date, self.assignee, self.children_ids, self.children, self.is_normalized, self.assigned_sprint_id)
    
    def __str__(self):
        
        # Want the mandatory components of each story's description to be printed first so that it lines up nicely with the other stories' descriptions and is easy to compare, whether or not every story has any of the optional components.
        story_description_components = ['\t{}'.format(self.id), str(self.size)]
        
        if self.assignee:
            assignee = self.assignee
        else:
            assignee = ''
        story_description_components.append(assignee)
        
        # Print the name last, as its length will probably vary the most
        if self.name:
            story_description_components.append(self.name)

        return'\t'.join(story_description_components)


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
    
    sprints, id_to_sprint_dict = load_sprint_data(input_dict)
    stories, id_to_story_dict = load_story_data(input_dict)

    return (sprints, id_to_sprint_dict, stories, id_to_story_dict)


def load_sprint_data(input_dict):

    sprints = []

    # Dictionary mapping sprint ID (a number) to the corresponding Sprint object
    id_to_sprint_dict = {}

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
        
        if 'assignee_capacities' in sprint_dict:
            sprint_constructor_args_dict['assignee_total_capacities'] = sprint_dict['assignee_capacities']

        # Now that we've assembled all the arguments, use them to create a new Sprint object and add it to the list of Sprint objects
        sprint = Sprint(**sprint_constructor_args_dict)
        sprints.append(sprint)
        id_to_sprint_dict[sprint.id] = sprint
    
    # To be safe, sort sprints by their end date (in ascending order)
    sprints.sort(key=attrgetter('end_date'))

    return (sprints, id_to_sprint_dict)


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
        
        if 'importance' in story_dict:
            story_constructor_args_dict['importance'] = story_dict['importance']
        
        if 'start_date' in story_dict:
            story_constructor_args_dict['start_date'] = convert_str_to_date(story_dict['start_date'])

        if 'end_date' in story_dict:
            story_constructor_args_dict['end_date'] = convert_str_to_date(story_dict['end_date'])
        
        if 'assignee' in story_dict:
            story_constructor_args_dict['assignee'] = story_dict['assignee']
        
        if 'prerequisite_for' in story_dict:
            story_constructor_args_dict['children_ids'] = story_dict['prerequisite_for']

        # Now that we've assembled all the arguments, use them to create a new Story object and add it to the list of Story objects
        story = Story(**story_constructor_args_dict)
        stories.append(story)
        id_to_story_dict[story.id] = story

    return (stories, id_to_story_dict)


# At this point, each story has a list of the (string) IDs of its children, but its list of the actual children themselves is empty -- populate the latter list with the children whose IDs are the corresponding elements in the former list.
def populate_children_from_ids(stories, id_to_story_dict):
    for story in stories:
        for child_id in story.children_ids:
            story.children.append(id_to_story_dict[child_id])


# If stories B and C both depend on A then, for consistency, we need to ensure that:
# a) A's importance value is >= max(B and C's importance values)
# b) A's end_date is <= (min(B and C's end dates) - 1 day)
#    NOTE: We make sure that A's end_date is at least 1 day before the earliest end_date of all the stories that depend on A to ensure that A is slotted out before the stories that depend on A (note that they can still end up in the same sprint together, but B/C should never end up in an EARLIER sprint than A)!
#
# If a story's importance and end_date adhere to the above rules regarding the corresponding values of its children, then we say that that story is 'normalized'.
def normalize_stories(stories):

    # children_values_dict is a dictionary mapping a tuple of story IDs [here: ('B', 'C')] to a tuple of their max importance and min end_date.
    children_values_dict = {}
    
    # For each story, calculate the max importance and min end_date of its children and potentially change its own importance and end_date based on those values (i.e. normalize the story).
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

    # See if the max importance and min end_date have already been calculated for this particular group of children.

    # If they have, then they will already be present in children_values_dict with a key formed from the IDs of the sorted list of children.
    key = tuple([child.id for child in children])
    if key in children_values_dict:
        max_importance, min_end_date = children_values_dict[key]
    
    # The max importance and min end_date have not already been calculated for this particular group of children.
    else:

        # First ensure each child is normalized
        for child in children:
            normalize_story(child, children_values_dict)
        
        # Then, using normalized importance and end_date values of all the children, calculate the max importance and min end_date for this group of children.
        max_importance = max([child.importance for child in children])
        min_end_date = min([child.end_date for child in children])

        # Now that we've calculated the max importance and min end_date for this group of children, save those values to save us time with any future parents of this same group of children.
        children_values_dict[key] = (max_importance, min_end_date)

    # Now that we've calculated the required values of this story's children, use them to normalize this story
    
    if story.importance < max_importance:
        story.importance = max_importance
    
    if story.end_date > (min_end_date - one_day):
        story.end_date = min_end_date - one_day

    # This story is now normalized
    story.is_normalized = True

    return


# Sort stories using the following algorithm:
# Given two stories A and B:
# If A is more important (has a higher importance value) than B, then A is sorted ahead of B.
# If their importance values are the same, but A has an earlier end_date than B, then A is sorted ahead of B.
# If their importance values and end dates are the same, but A is bigger than B, then A is sorted ahead of B.
def sort_stories(stories):

    # To get the resulting order we want, we need to sort by the LEAST important attribute first!

    # Sort stories by size in descending order
    stories.sort(key=attrgetter('size'), reverse=True)

    # Sort resulting stories by end_date in ascending order
    stories.sort(key=attrgetter('end_date'))
    
    # Sort resulting stories by importance in descending order
    stories.sort(key=attrgetter('importance'), reverse=True)


# Slot stories into sprints, following the order of the 'stories' list (if story A appears before story B in the 'stories' list, then A will be slotted into a sprint before B) and the 'sprints' list (if sprint 1 appears before sprint 2 in the 'sprints' list, then we will attempt to slot stories into sprint 1 before sprint 2)
# Note that, depending on how much space is left in each sprint, even though we try to slot story A into one of the sprints before trying to slot story B, if B is smaller than A, B might end up in an earlier sprint than A (i.e. if that sprint didn't have enough space for A, forcing A to go to the next sprint, but had enough space for B).
# Thus, even though we have ensured (via normalization and sorting) that, if A is the parent of B, A appears before B in the sorted list of stories, that alone is NOT enough to guarantee that, after slotting the stories, B will not end up in an earler sprint than its parent A! Instead, as seen below, we might need to modify B's start date as well.
def slot_stories(stories, sprints, id_to_sprint_dict, max_date=MAX_DATE):

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

        for sprint in available_sprints:

            # Try to slot the story into the first sprint that has enough space for it, and that abides by its start and end date constraints
            if (sprint.available_capacity >= story_size) \
                and (sprint.end_date >= story.start_date) \
                and (sprint.start_date <= story.end_date):

                # If the story is already assigned to someone, only slot it in this sprint if that person has enough available capacity in this sprint
                # Note that assignee can be None, but assignee_available_capacities will always be a valid dict.
                assignee = story.assignee
                assignee_available_capacities = sprint.assignee_available_capacities
                if assignee in assignee_available_capacities:
                    if assignee_available_capacities[assignee] >= story_size:
                        assignee_available_capacities[assignee] -= story_size
                    else:
                        # Do not slot this story in this sprint, because the assignee does not have enough capacity to do it in this sprint
                        continue

                # Slot story into sprint
                sprint.stories.append(story)
                sprint.available_capacity -= story_size
                available_stories.remove(story)
                story.assigned_sprint_id = sprint.id
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

        # Thanks to normalization and story sorting, we know that, if this story has children, we have not yet attempted to slot them into a sprint yet. 
        # If any of this story's children is smaller than this story, it might accidentally end up slotted into a sprint before this story -- i.e. the sprint schedule might end up calling for the child to be done before the parent! 
        # To avoid this, after having attempted to slot this story above, we modify each of its children's start date below.
        for child in story.children:

            # If this story was assigned to a sprint, ensure that all the children's start dates are no earlier than the start of that sprint -- i.e. ensure that the children cannot be assigned to a sprint prior to the sprint that their parent was assigned to.
            if story.assigned_sprint_id:
                assigned_sprint = id_to_sprint_dict[story.assigned_sprint_id]
                earliest_start_date_for_children = assigned_sprint.start_date
            
            # If this story was not assigned to any sprint, its children cannot be allowed to be assigned to any sprint either! 
            # The easiest way to achieve this is to set their start dates to a date guaranteed to be after the very last sprint's end date.
            else:
                earliest_start_date_for_children = max_date

            if child.start_date < earliest_start_date_for_children:
                child.start_date = earliest_start_date_for_children

    # Enter this 'else' clause if we did NOT exit the above 'for' loop by breaking out of it.
    else:

        # It is possible to have stories remaining (unslotted) without having already placed them in remaining_stories:
        #   a) If there is not enough space in the remaining sprints to slot in the remaining stories, but the remaining sprints are NOT full!
        #   b) If the last sprint was perfectly filled when the final story in the 'stories' list was slotted in -- note that there are still other unslotted stories in the 'stories' list, but there wasn't enough space to slot them in, so they were skipped over before we got to this final story.
        if available_stories:
            remaining_stories = available_stories
    
    return remaining_stories