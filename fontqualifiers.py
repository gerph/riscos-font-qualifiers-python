"""
Parser for font qualifiers in a font string.

Font qualifiers are supplied within a font string. The FontQualifiers class is able to parse the
font qualifiers to extract the information held within them.

Usage details:

    fq = FontQualifiers(font_string, need_trailing_space_on_matrix=False)

        - This is equivalent to the processing used by Font_FindFont.
        - Note: Classic FontManager allows font qualifiers without trailing spaces, whilst the
                PRM states that they are required. The boolean flag allows this to be configured.

    fq.apply_fields(second_font_string, need_trailing_space_on_matrix=False))

        - This is equivalent to the processing used by Font_ApplyFields.
        - Note: Again, the trailing spaces can be configured for the secondary string.

    offset = FontQualifiers.find_field(font_string, qualifier)

        - Locates the offset in the string of the qualifier character.
        - Does not parse the string; as it must return offsets within the original string.
"""

import re


# Identifiers which can be used in the string
acceptable_identifiers_re = re.compile(r'^[\x21-\x7e]+$')


class FontQualifiersError(Exception):
    """
    Parent class for all font identifier errors.
    """
    pass

class FontQualifiersBadStringError(FontQualifiersError):
    pass


class FontQualifiersBadMatrixError(FontQualifiersError):
    pass


class FontQualifierEmpty(object):
    """
    A placeholder for an empty field in a font qualifier.
    """
    pass


class FontQualifiers(object):
    """
    Object to hold the parsed font identifier.

    Properties:

        fontid:         The actual font identifier
        fontlocal:      Font with a specific local name, in the form of a tuple (territory, name)
        encodinglocal:  Encoding with a specific local name, in the form of a tuple (territory, name)
        encoding:       Encoding name.
        matrix:         Transformation matrix as a tuple of 6 values, as floating point numbers
                        converted from the standard 16.16 matrix values for the scaling factors,
                        and in 1000s of an em for the offsets.
    """

    def __init__(self, font_string, need_trailing_space_on_matrix=False, allow_empty=False):
        """
        Parse a font string to create properties of the font.

        @param fontid:      The font identifier to parse
        @param need_trailing_space_on_matrix: Whether the trailing space on the matrix is acceptable
        @param allow_empty: Allow a field to be supplied with an empty string (used internally for
                            removing fields in apply_fields)
        """
        self.fontid = None
        self.fontlocal = None
        self.encoding = None
        self.encodinglocal = None
        self.matrix = None

        self.parse(font_string, need_trailing_space_on_matrix, allow_empty)

    def __repr__(self):
        parts = [('fontid', self.fontid),
                 ('fontlocal', self.fontlocal),
                 ('encoding', self.encoding),
                 ('encodinglocal', self.encodinglocal),
                 ('matrix', self.matrix)]
        parts = [part for part in parts if part[1] is not None]
        def value(p):
            if p is FontQualifierEmpty:
                return '<empty>'
            else:
                return repr(p)
        parts = ["{}={}".format(part[0], value(part[1])) for part in parts]
        return "<{}({})>".format(self.__class__.__name__,
                                 ', '.join(parts))

    def __str__(self):
        return self.font_string

    @property
    def font_string(self):
        """
        Create a font string from the properties.
        """
        fields = []
        if self.fontid is not None and self.fontid is not FontQualifierEmpty:
            fields.append(('F', self.fontid))
        if self.fontlocal is not None and self.fontlocal is not FontQualifierEmpty:
            fields.append(('f', '{} {}'.format(self.fontlocal[0], self.fontlocal[1])))

        if self.encoding is not None and self.encoding is not FontQualifierEmpty:
            fields.append(('E', self.encoding))
        if self.encodinglocal is not None and self.encodinglocal is not FontQualifierEmpty:
            fields.append(('e', '{} {}'.format(self.encodinglocal[0], self.encodinglocal[1])))

        if self.matrix is not None and self.matrix is not FontQualifierEmpty:
            # We always include the trailing space when generating the string as this string
            # may need to be stored in a document that is used on a system which conforms to
            # the PRM.
            fields.append(('M', '{} {} {} {} {} {} '.format(int(self.matrix[0] * 65536),
                                                            int(self.matrix[1] * 65536),
                                                            int(self.matrix[2] * 65536),
                                                            int(self.matrix[3] * 65536),
                                                            int(self.matrix[4] * 1000),
                                                            int(self.matrix[5] * 1000))))

        if len(fields) == 1 and fields[0][0] == 'F':
            # There is only the font name, so we may as well return it as a bare font name;
            # there's no point in returning it with the qualifier prepended
            return fields[0][1]

        parts = ['\\{}{}'.format(field[0], field[1]) for field in fields]
        return ''.join(parts)

    def parse(self, font_string, need_trailing_space_on_matrix=False, allow_empty=False):
        font_string = font_string or ''

        if font_string == '' and allow_empty:
            # This means that there are no fields to apply, so we can return with nothing set
            return

        if font_string == '' or font_string[0] != '\\':
            font_string = '\\F' + font_string

        parts = font_string.split('\\')
        # The first part will be empty

        for part in parts[1:]:
            qualifier = part[0]
            part = part[1:]
            if qualifier == 'F':
                if part == '' and allow_empty:
                    self.fontid = FontQualifierEmpty
                else:
                    self.fontid = part
                    if not acceptable_identifiers_re.search(part):
                        raise FontQualifiersBadStringError("Invalid font name in '%s'" % (part,))

            elif qualifier == 'f':
                if part == '' and allow_empty:
                    self.fontlocal = FontQualifierEmpty
                else:
                    if ' ' not in part:
                        raise FontQualifiersBadStringError("Cannot parse font name qualifier in '%s'" % (part,))
                    (territory, name) = part.split(' ', 1)
                    try:
                        territory = int(territory)
                    except ValueError:
                        raise FontQualifiersBadStringError("Cannot parse font name qualifier with invalid territory in '%s'" % (part,))
                    self.fontlocal = (territory, name)

            elif qualifier == 'E':
                if part == '' and allow_empty:
                    self.encoding = FontQualifierEmpty
                else:
                    self.encoding = part
                    if not acceptable_identifiers_re.search(part):
                        raise FontQualifiersBadStringError("Invalid encoding name qualifier in '%s'" % (part,))

            elif qualifier == 'e':
                if part == '' and allow_empty:
                    self.encodinglocal = FontQualifierEmpty
                else:
                    if ' ' not in part:
                        raise FontQualifiersBadStringError("Cannot parse font encoding qualifier in '%s'" % (part,))
                    (territory, name) = part.split(' ', 1)
                    try:
                        territory = int(territory)
                    except ValueError:
                        raise FontQualifiersBadStringError("Cannot parse font encoding qualifier with invalid territory in '%s'" % (part,))
                    self.encodinglocal = (territory, name)

            elif qualifier == 'M':
                if part == '' and allow_empty:
                    self.matrix = FontQualifierEmpty
                else:
                    # This is a matrix request.
                    # These have the form of 6 decimal integers separated by a space (and with a trailing space)
                    # The PRM states 'Each number - including the last one - must be followed by a space.'.
                    # This is NOT true; the final character of the qualifier need not be a space.
                    # So we allow this to be parsed as acceptable.
                    part = part.lstrip(' ')
                    matrix_parts = part.split(' ')
                    if matrix_parts and matrix_parts[-1] == '':
                        # IF there's a trailing space, trim it.
                        matrix_parts.pop()
                    else:
                        if need_trailing_space_on_matrix:
                            raise FontQualifiersBadMatrixError("Cannot parse font matrix without trailing space in '%s'" % (part))

                    if len(matrix_parts) != 6:
                        raise FontQualifiersBadMatrixError("Cannot parse font matrix with %i components in '%s'" % (len(matrix_parts), part))
                    try:
                        # FIXME: Check whether this should actually be a value from OS_ReadUnsigned? ie 16_10000 is valid?
                        values = [int(value) for value in matrix_parts]
                        if any((value >= (1<<31) for value in values)):
                            raise FontQualifiersBadMatrixError("Cannot value too large in font matrix '%s'" % (part,))
                        if any((value <= -(1<<31) for value in values)):
                            raise FontQualifiersBadMatrixError("Cannot value too large in font matrix '%s'" % (part,))
                        matrix = [value / 65536.0 if index < 4 else value / 1000.0 for index, value in enumerate(values)]
                    except ValueError:
                        raise FontQualifiersBadMatrixError("Cannot parse font matrix values as integers in '%s'" % (part))
                    self.matrix = matrix

            else:
                raise FontQualifiersBadStringError("Cannot parse qualifier '%s'" % (qualifier,))

    def apply_fields(self, font_string, need_trailing_space_on_matrix=False):
        """
        Apply fields from a second font string to a set of qualifiers.

        The fields in the second font string may include an empty field for the qualifier to
        remove the field. The classic FontManager operates on these strings as bare elements,
        whereas we will process the strings into their constituents every time.
        """
        apply = FontQualifiers(font_string,
                               need_trailing_space_on_matrix=need_trailing_space_on_matrix,
                               allow_empty=True)

        def reduce(current_value, new_value):
            """
            If new empty field was given, the value is unset; if new value given, use it, otherwise use original.
            """
            if new_value is FontQualifierEmpty:
                return None
            if new_value is not None:
                return new_value
            return current_value

        self.fontid = reduce(self.fontid, apply.fontid)
        self.fontlocal = reduce(self.fontlocal, apply.fontlocal)
        self.encoding = reduce(self.encoding, apply.encoding)
        self.encodinglocal = reduce(self.encodinglocal, apply.encodinglocal)
        self.matrix = reduce(self.matrix, apply.matrix)

    @staticmethod
    def find_field(font_string, wanted):
        """
        Find a given field by its qualifier character.

        Note: Does not validate the string at all.

        @return: offset of the qualifier's value in the string or None if not present
        """
        if not font_string:
            return None

        offset = 0
        if font_string[0] != '\\' and wanted == 'F':
            return 0

        parts = font_string.split('\\')
        offset = len(parts[0])
        for part in parts[1:]:
            offset += 2
            qualifier = part[0]
            if qualifier == wanted:
                return offset
            offset += len(part) - 1

        return None
