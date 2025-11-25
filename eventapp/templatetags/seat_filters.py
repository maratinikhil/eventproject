from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    return dictionary.get(key)

@register.filter
def group_by_row(seats):
    """Group seats by row and return sorted rows"""
    rows = {}
    for seat in seats:
        if seat.row not in rows:
            rows[seat.row] = []
        rows[seat.row].append(seat)
    
    # Sort seats within each row by number
    for row_seats in rows.values():
        row_seats.sort(key=lambda x: x.number)
    
    # Return sorted rows
    return sorted(rows.items())