from django.dispatch import Signal


class GroupOverview(object):
    pass


# In Django 4+ and 5, we don't need providing_args anymore
show_group_overview = Signal()