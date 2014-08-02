####
# Base Validation error
##

import re


# Here, I had to change the superclass to ValueError, since it calls
# the ValueError constructor which expects a ValueError instance where
# we pass self
import unittest


class ValidationException(ValueError):
    def __init__(self, *args, **kwargs):
        self.error_dict = kwargs.pop('error_dict', None)
        ValueError.__init__(self, *args, **kwargs)

####
# ValidatorType -- base class for all validation types
##
def is_empty(value):
    return not value


class ValidatorType:
    def __init__(self, *args, **kwargs):
        pass

    def to_python(self, value):
        if is_empty(value):
            return None
        return self._to_python(value)

    def _to_python(self, value):
        return value

class Integer(ValidatorType):
    def __init__(self, *args, **kwargs):
        self.min = kwargs.pop('min', None)
        self.max = kwargs.pop('max', None)

        ValidatorType.__init__(self, *args, **kwargs)

    def _to_python(self, value):
        try:
            value = int(value)
        except ValueError, e:
            raise ValidationException('invalid value')

        if self.min and value < self.min:
            raise ValidationException('value must not be less than %d' % self.min)

        if self.max and value > self.max:
            raise ValidationException('value must not be greater than %d' % self.max)

        return value

class String(ValidatorType):
    def __init__(self, length, *args, **kwargs):
        self.length = length
        ValidatorType.__init__(self, *args, **kwargs)

    def _to_python(self, value):
        # Ensure this object can be converted to a string, and does not
        # exceed the length limit
        try:
            value = str(value)
        except ValueError, e:
            raise ValidationException('invalid value')

        if len(value) > self.length:
            raise ValidationException("value's length must not be greater than %d" % self.length)

        return value

class Email(ValidatorType):
    def _to_python(self,value):
        try:
            value = str(value)
        except ValueError, e:
            raise ValidationException('invalid value')
        # Basic check for valid-ish email address. The REGEX to validate a
        # standards-compliant address is notorious complex and naive
        # implementations may exclude valid addresses, so this will be a very
        # basic check to make sure the user did not clearly enter the wrong
        # thing. ___@___.___
        if not re.match(r"^.+[@].+[.].+$", value):
            raise ValidationException('invalid email address')
        return value

class FormField:
    def __init__(self, type=None, name=None, empty=False):
        self.name = name
        self.type = type
        self.empty = empty

    def get_default(self):
        return None

    def to_python(self, value):
        if self.type:
            value = self.type.to_python(value)
        return value

class FieldExtractor(type):
    def __init__(cls, classname, bases, dict):
        type.__init__(cls, classname, bases, dict)

        cls._fields = {}

        for k,v in dict.items():
            if isinstance(v, FormField):
                v.name = v.name or k
                cls._fields[k] = v

class FormProcessor(object):
    __metaclass__ = FieldExtractor

    def __init__(self, form_name=None):
        self.form_name = form_name
        object.__init__(self)

    def __validate_fields(self, values):
        errors = {}

        # For each item in the values dict
        for field_name, value in values.iteritems():
            # Find the FormField associated with this name
            try:
                form_field = self._fields[field_name]
            except KeyError, e:
                raise ValidationException("invalid field %s" % field_name)
                errors[field_name] = e
                continue
            try:
                values[field_name] = form_field.to_python(value)
            except ValidationException, e:
                errors[field_name] = e

        return (values, errors)

    def process(self, values):
        if self.form_name is not None and ('__form_name' not in values or values['__form_name'] != self.form_name):
            return None
        (values, errors) = self.__validate_fields(values)

        if errors:
            raise ValidationException(error_dict=errors)
        return values

class MyFormProcessor(FormProcessor):
    first_name = FormField(String(16))
    last_name = FormField(String(16))
    email = FormField(Email())
    age = FormField(Integer(min=18))

class TestFormProcessor(unittest.TestCase):
    def setUp(self):
        self.mfp = MyFormProcessor()

    def test_invalid_email(self):
        self.assertRaises(ValidationException, self.mfp.process, {'email': 'dave.smithemail.com'})

    def test_valid_email(self):
        self.mfp.process({'email': 'dave.smith@email.com'})

    def test_invalid_first_name(self):
        self.assertRaises(ValidationException, self.mfp.process, {'first_name': 'davewithareallylongname'})

    def test_valid_first_name(self):
        self.mfp.process({'first_name': 'dave'})

if __name__ == '__main__':
    mfp = MyFormProcessor()
    print mfp.process({'first_name': 'dave',
                       'last_name': 'smith',
                       'email': 'dave.smith@email.com',
                       'age': '32'})

    unittest.main()
