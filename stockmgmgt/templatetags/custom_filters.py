from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, {}).get('quantity', 0)  # Retorna 0 se não existir
