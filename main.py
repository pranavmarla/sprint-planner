#! /usr/bin/env python3

__author__ = 'Pranav Marla'


from datetime import date, datetime
import lib


input_file_path = lib.parse_command_line_args()

sprints, stories, id_to_story_dict = lib.load_input_data(input_file_path)

# Populate list of children
lib.populate_children_from_ids(stories, id_to_story_dict)


#! DEBUG
# print('Stories, after populating kids, before normalizing:\n')
# for story in stories:
#     print('\t{}\n'.format(story))
# print()


# Normalize stories
lib.normalize_stories(stories)


#! DEBUG
# print('Stories, after normalizing, before sorting:\n')
# for story in stories:
#     print('\t{}\n'.format(story))
# print()


# Sort stories
lib.sort_stories(stories)


#! DEBUG
# print('Stories, after sorting:')
# for story in stories:
#     print('\t{}'.format(story))
# print()


# Slot stories
remaining_stories = lib.slot_stories(stories, sprints)



print('Sprints, after slotting in stories:')
for sprint in sprints:
    print('-------------')
    print('Sprint {}:\tCapacity remaining: {}/{}\n'.format(sprint.id, sprint.available_capacity, sprint.total_capacity))
    
    for story in sprint.stories:
        print(story)
    print()

    if sprint.assignee_total_capacities:
        print('\t-------------\n')
        print('\tAssignees:')
        for assignee, assignee_remaining_capacity in sprint.assignee_available_capacities.items():
            print('\t\t{}: {}/{} remaining'.format(assignee, assignee_remaining_capacity, sprint.assignee_total_capacities[assignee]))
        print()

    print('-------------\n')

if remaining_stories:
    print('The following stories could not be slotted into any sprint:')
    for story in remaining_stories:
        print(story)
else:
    print('All stories were successfully slotted into sprints!')

print()
