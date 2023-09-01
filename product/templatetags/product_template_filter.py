from django import template

register = template.Library()


@register.filter(name='watch_quantity_checker')
def watch_quantity_checker(quantity):
    if quantity <= 3:
        return True
    else:
        return False
