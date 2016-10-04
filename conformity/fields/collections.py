from __future__ import unicode_literals
import six

from .basic import Base


class List(Base):
    """
    A list of things of a single type.
    """

    def __init__(self, contents, max_length=None, min_length=None):
        self.contents = contents
        self.max_length = max_length
        self.min_length = min_length

    def errors(self, value):
        if not isinstance(value, list):
            return ["Not a list"]
        result = []
        if self.max_length is not None and len(value) > self.max_length:
            result.append("List longer than %s" % self.max_length)
        elif self.min_length is not None and len(value) < self.min_length:
            result.append("List is shorter than %s" % self.min_length)
        for i, element in enumerate(value):
            result.extend(
                "Index %i: %s" % (i, error)
                for error in (self.contents.errors(element) or [])
            )
        return result


class Dictionary(Base):
    """
    A dictionary with types per key (and requirements per key).
    """

    def __init__(self, contents, optional_keys=None, ignore_extra_keys=False):
        self.contents = contents
        self.optional_keys = optional_keys or []
        self.ignore_extra_keys = ignore_extra_keys

    def errors(self, value):
        if not isinstance(value, dict):
            return ["Not a dict"]
        result = []
        seen_keys = set()
        for key, field in self.contents.items():
            # Check key is present
            if key not in value:
                if key not in self.optional_keys:
                    result.append("Key %s missing" % key)
            else:
                seen_keys.add(key)
                # Check key type
                result.extend(
                    "Key %s: %s" % (key, error)
                    for error in (field.errors(value[key]) or [])
                )
        # Check for extra keys
        extra_keys = set(value.keys()) - set(self.contents.keys())
        if extra_keys and not self.ignore_extra_keys:
            result.append("Extra keys %s present" % (", ".join(six.text_type(key) for key in extra_keys)))
        return result