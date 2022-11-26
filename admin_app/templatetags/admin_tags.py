from django import template

register = template.Library()

@register.filter(name='tournament_type_at_index')
def tournament_type_at_index(tournaments, index):
    return tournaments[int(index)].type.type

@register.filter(name='tournament_state_at_index')
def tournament_state_at_index(tournaments, index):
    return tournaments[int(index)].get_state_display()

@register.filter(name='get_type')
def get_type(value):
    return type(value).__name__

@register.filter(name='dict_access')
def dict_access(table, value):
    return table[value]
