def create_illegal_type_error(found_type, *needed_types):
    required = ' or '.join(str(ntype) for ntype in needed_types)
    return ValueError(f'{required} was required but {found_type} was found')


class Property:
    def __init__(self, display=True, user_edit=True, nullable=True):
        self.display = display
        self.user_edit = user_edit
        self.nullable = nullable
    
    def get_value(self):
        return self.get_value
    
    def set_value(self, new_value):
        if self.nullable or new_value is not None:
            self.value = new_value
        else:
            raise ValueError('Value cannot be None')
    
    def to_dict(self):
        return { 'nullable': self.nullable, 'display': self.display, 'user_edit': self.user_edit, 'value': self.value}


class StringProperty(Property):
    def __init__(self, value, display=True, user_edit=True, nullable=True):
        super(StringProperty, self).__init__(display=display, user_edit=user_edit, nullable=nullable)
        self.set_value(value)
    
    def set_value(self, new_value):
        if isinstance(new_value, (str, type(None))):
            super(StringProperty, self).set_value(new_value)
        else:
            raise create_illegal_type_error(type(new_value), str)


class BoundedProperty(Property):
    def __init__(self, value, min, max, display=True, user_edit=True, nullable=True):
        super(BoundedProperty, self).__init__(display=display, user_edit=user_edit, nullable=nullable)
        self.min = min
        self.max = max
        self.set_value(value)
    
    def set_value(self, new_value):
        if new_value is not None:
            if new_value > self.max:
                raise ValueError(f'{new_value} is larger than {self.max}')
            elif new_value < self.min:
                raise ValueError(f'{new_value} is smaller than {self.min}')
        super(BoundedProperty, self).set_value(new_value)
    
    def to_dict(self):
        data_dict = super(BoundedProperty, self).to_dict()
        data_dict['min'] = self.min
        data_dict['max'] = self.max
        return data_dict


class NumericProperty(Property):
    def __init__(self, value, display=True, user_edit=True, nullable=True):
        super(StringProperty, self).__init__(display=display, user_edit=user_edit, nullable=nullable)
        self.set_value(value)
    
    def set_value(self, new_value):
        if isinstance(new_value, (int, float, type(None))) and not isinstance(new_value, bool):
            super(NumericProperty, self).set_value(new_value)
        else:
            raise create_illegal_type_error(type(new_value), int, float)


class BooleanProperty(Property):
    def __init__(self, value, display=True, user_edit=True, nullable=True):
        super(StringProperty, self).__init__(display=display, user_edit=user_edit, nullable=nullable)
        self.set_value(value)
    
    def set_value(self, new_value):
        if isinstance(new_value, (bool, type(None))):
            super(BooleanProperty, self).set_value(new_value)
        else:
            raise create_illegal_type_error(type(new_value), bool)

