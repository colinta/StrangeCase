"""
Provides "commas" formatter function, which adds commas.

    {my.age | commas} => 1,024
"""

def commas(value):
    return f"{int(value):,}"
