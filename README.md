# RISC OS Font qualifier parsing in Python

This repository contains a class for parsing font qualifiers from a font string, in Python.
It is part of the Pyromaniac font system, and provides support for the SWIs which operate
on the font strings:

* `Font_FindFont` - parses the font strings into qualifiers internaller.
* `Font_ApplyFields` - allows one font string to be applied to another, possibly with elements removed.
* `Font_FindField` - allows the offset of a given field qualifier to be located in a string.


## Usage

```
fq = FontQualifiers(font_string, need_trailing_space_on_matrix=False)
```

This is equivalent to the processing used by Font_FindFont.

Note: Classic FontManager allows font qualifiers without trailing spaces, whilst the
PRM states that they are required. The boolean flag allows this to be configured.

```
fq.apply_fields(second_font_string, need_trailing_space_on_matrix=False))
```

This is equivalent to the processing used by Font_ApplyFields.
Note: Again, the trailing spaces can be configured for the secondary string.

```
offset = FontQualifiers.find_field(font_string, qualifier)
```

Locates the offset in the string of the qualifier character. Does not parse the string; as it must return offsets within the original string.


## Tests

Tests exist to show that the module is working properly, intended for use on GitLab.
Code coverage is reported as well.

To test, use:

```
make tests PYTHON=python2
make tests PYTHON=python3
```

To run coverage, use:

```
make coverage
```
