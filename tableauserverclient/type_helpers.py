def item_type(obj):
    return type(obj).__name__.replace('Item', '').lower()
