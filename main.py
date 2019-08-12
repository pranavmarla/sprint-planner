#! /usr/bin/python3

__author__ = 'Pranav Marla'


from datetime import date, datetime
import lib

Sprint = lib.Sprint
Story = lib.Story

sprints = \
    [
        Sprint(date(2019, 1, 24), 15),
        Sprint(date(2019, 1, 28), 15)
    ]

# sprints = \
#     [
#         Sprint(date(2019, 1, 24), 20),
#         Sprint(date(2019, 1, 28), 20)
#     ]

print('Sprints:')
for sprint in sprints:
    print('\t{}'.format(sprint))
print()

stories = \
    [
        Story(id='M', size=1, priority=-1, deadline=date(2019, 1, 28)),
        Story(id='L', size=3, priority=1, deadline=date(2019, 1, 28)),
        Story(id='K', size=5, priority=-1, deadline=date(2019, 1, 28)),
        Story(id='J', size=5, priority=0, deadline=date(2019, 1, 28)),
        Story(id='I', size=2, priority=-1, deadline=date(2019, 1, 28)),
        Story(id='H', size=3, priority=1, deadline=date(2019, 1, 28)),
        Story(id='G', size=3, priority=0, deadline=date(2019, 1, 28)),
        Story(id='F', size=5, priority=1, deadline=date(2019, 1, 27), children=['G', 'H', 'I']),
        Story(id='E', size=3, priority=1, deadline=date(2019, 1, 26), children=['F']),
        Story(id='D', size=5, priority=1, deadline=date(2019, 1, 26)),
        Story(id='C', size=3, priority=1, deadline=date(2019, 1, 25), children=['D']),
        Story(id='B', size=2, priority=1, deadline=date(2019, 1, 24), children=['C']),
        Story(id='A', size=5, priority=1, deadline=date(2019, 1, 28))
    ]

print('Stories, before sorting:')
for story in stories:
    print('\t{}'.format(story))
print()

lib.sort_stories(stories)

print('Stories, after sorting:')
for story in stories:
    print('\t{}'.format(story))
print()

overflow_stories = lib.slot_stories(stories, sprints)

print('Sprints, after slotting in stories:')
for sprint in sprints:
    print('---')
    print('Sprint {}:\tCapacity remaining: {}/{}\n'.format(sprint.id, sprint.available_capacity, sprint.total_capacity))
    for story in sprint.stories:
        print('\t{}'.format(story.id))
    print('---\n')
print()

if overflow_stories:
    print('The following stories could not be slotted into any sprint:')
    for story in overflow_stories:
        print('\t{}'.format(story.id))
else:
    print('All stories were successfully slotted into sprints!')
