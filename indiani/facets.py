"""Filterable facets for restaurants.

Each restaurant lists the facet keys that apply in its ``attrs`` field. The card
renderer turns them into badges and the index page builds one filter chip per
facet that actually appears in the data. Adding a facet here plus to a
restaurant's ``attrs`` is all that is needed, no other code changes.

``ayce`` is special: it also shows the laughing-Buddha sticker on the card.
"""

# key -> (emoji, label, badge CSS classes for the small pill on the card)
FACETS = {
    'ayce': {
        'emoji': '🍽️',
        'label': 'All you can eat',
        'cls': 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',
    },
}

# Order in which chips/badges are rendered.
FACET_ORDER = ['ayce']

# Rating threshold for the "Top hodnocené" filter chip.
TOP_RATING = 4.5
