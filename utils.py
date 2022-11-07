def is_iterable(x):
    """Test a variable for iterability.
    Determine whether an object ``x`` is iterable. In Python 2, this
    was as simple as checking for the ``__iter__`` attribute. However, in
    Python 3, strings became iterable. Therefore, this function checks for the
    ``__iter__`` attribute, returning True if present (except for strings,
    for which it will return False).
    Parameters
    ----------
    x : str, iterable or object
        The object in question.
    Examples
    --------
    Strings and other objects are not iterable:
    >>> x = "not me"
    >>> y = 123
    >>> any(is_iterable(v) for v in (x, y))
    False
    Tuples, lists and other structures with ``__iter__`` are:
    >>> x = ('a', 'tuple')
    >>> y = ['a', 'list']
    >>> all(is_iterable(v) for v in (x, y))
    True
    This even applies to numpy arrays:
    >>> import numpy as np
    >>> is_iterable(np.arange(10))
    True
    Returns
    -------
    isiter : bool
        True if iterable, else False.
    """
    if isinstance(x, str):
        return False
    return hasattr(x, '__iter__')
