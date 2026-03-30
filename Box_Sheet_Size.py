from enum import Enum
from pint import UnitRegistry
import math
ureg = UnitRegistry()
mm = ureg.mm
cm = ureg.cm
inch = ureg.inch
m = ureg.m

def convert_to_inches(length, width, height, units):
    """
    Convert the given value to inches based on the specified units.

    Args:
        value (float): The value to convert.
        units (str): The units of the value ('cm', 'm', or 'inch').

    Returns:
        float: The value in inches.
    """
    length = length * units
    width = width * units
    height = height * units
    # Convert dimensions to the same unit (inch in this case)
    if not units == inch:
        length = length.to(inch)
        width = width.to(inch)
        height = height.to(inch)
    return length, width, height

def calculate_sheet_size(length, width, height, boxtype, units):
    """
    Calculate the sheet size required for a box given its dimensions.

    Args:
        length (float): The length of the box.
        width (float): The width of the box.
        height (float): The height of the box.

    Returns:
        float: The total sheet size required.
    """

    if boxtype == BoxType.Universal:
        # Universal box type calculation
        sheet_width = (height + width) + 1*inch
        sheet_length = 2 * (length + width ) + 1.5*inch

    elif boxtype == BoxType.Bottom_Locking:
        # Bottom locking box type calculation
        sheet_length = height + 1.5 * width + 2*inch
        sheet_width = 2 * (length + width) + 1*inch
    
    elif boxtype == BoxType.Mobile_Type:
        # Mobile type box calculation
        sheet_length = 4 * height + length + 1*inch    
        sheet_width = 2 * (height + width) + height + 1*inch
    
    elif boxtype == BoxType.Ring_Flap:
        # Ring flap box calculation
        sheet_length = max ( 2 * (height.magnitude + width.magnitude) + 2,     2 * width.magnitude + length.magnitude + 2) * inch
        sheet_width = height + length + 2.5*inch 

    sheet_length = math.ceil(sheet_length.magnitude) * inch
    sheet_width = math.ceil(sheet_width.magnitude) * inch

    sheet_size = [sheet_length, sheet_width]
    return sheet_size

class BoxType(Enum):
    """
    Enum for different box types.
    """
    Universal = 1
    Bottom_Locking = 2
    Mobile_Type = 3,
    Ring_Flap = 4

if __name__ == "__main__":
    # Input dimensions for the box
    length = 15
    width = 10
    height = 5
    boxtype = BoxType.Universal
    units = inch

    # Convert dimensions to inches
    length, width, height = convert_to_inches(length, width, height, units)
    
    sheet_size = calculate_sheet_size(length, width, height, boxtype, units)

    print(f"Sheet size required for the box: {sheet_size[0]} x {sheet_size[1]}")

    # # Calculate and display the sheet size
    # for boxtype in BoxType:
    #     sheet_size = calculate_sheet_size(length, width, height, boxtype, units)
    #     print({boxtype})
    #     if boxtype == BoxType.Bottom_Locking:
    #         print("2 Up Locking Sheet Size = ", math.ceil((2 * sheet_size[0] - (width/2 - 1 * inch)).magnitude), "x", math.ceil(((2 * sheet_size[1]) - (length + width)).magnitude), "inches")
    #     print(f"Sheet size required for the box: {sheet_size[0]} x {sheet_size[1]}")