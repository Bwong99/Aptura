from django import template

register = template.Library()

@register.filter
def genre_icon(genre):
    icons = {
        'landscape': '🏔️',
        'portrait': '👤',
        'city': '🏙️',
        'street': '🛣️',
        'nature': '🌿',
        'pet': '🐾',
        'architecture': '🏛️',
        'drone': '🚁',
        'wedding': '💒',
        'fashion': '👗',
        'sports': '⚽',
        'documentary': '📸',
        'product': '📦',
        'food': '🍽️',
        'abstract': '🎨',
    }
    return icons.get(genre, '📷')
