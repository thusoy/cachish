def merge_dicts(a, b):
    '''Merge dictionaries in an additive way, ie. only enable b to override leaf
    keys.

    The contents of b will be added to a inline.
    '''
    # pylint: disable=invalid-name
    for key, value in b.items():
        existing_key = a.get(key)
        if isinstance(existing_key, dict):
            merge_dicts(existing_key, value)
        else:
            a[key] = value
