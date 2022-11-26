from django import template

register = template.Library()

# @register.filter
# def keyvalue(dict, key):    
#     try:
#         return dict[key]
#     except KeyError:
#         return key

@register.simple_tag
def update_var(value):
    """ Update an existing template variable """
    return value

@register.filter()
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False