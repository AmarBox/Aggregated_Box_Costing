from enum import Enum
from pint import UnitRegistry
import math
ureg = UnitRegistry()
ureg.define('INR = [currency]')
cm = ureg.cm
g = ureg.g
kg = ureg.kg
inch = ureg.inch
m = ureg.m
INR = ureg.INR


def get_inputs (length, width, height, paper_quality, ply_num):
   
    # Ensure all inputs are integers
    length = int(input("Enter the length: "))
    width = int(input("Enter the width: "))
    paper_quality = int(input("Enter the paper quality: "))
    ply_num = int(input("Enter the ply number: "))
    if ply_num % 2 == 0:
        raise ValueError("Ply number must be odd")
    
    if not all(isinstance(i, int) for i in [length, width, paper_quality, ply_num]):
        raise ValueError("Length, width, height, paper_quality, and ply_num must be integers")
    
    print(f"Length: {length}, Width: {width}, Height: {height}, Paper Quality: {paper_quality}, Ply Num: {ply_num}")

def sheet_area (length, width, height):
    
    sheet_length = (2 * (length + width) + 1) * inch
    sheet_height = (height + width) * inch
    sheet_area = sheet_length * sheet_height
    return sheet_area

def sheet_area_cms (length, width):

    sheet_length = length * cm
    sheet_height = width * cm
    sheet_area = sheet_length * sheet_height
    return sheet_area

def sheet_area_inches (length, width):

    sheet_length = length * inch
    sheet_height = width * inch
    sheet_area = sheet_length * sheet_height
    return sheet_area

def sheet_weight (sheet_area, paper_weight, ply_num):
    
    backing_weight = int((ply_num/2))*paper_weight[0] * g/m**2
    fluting_weight = int((ply_num/2))*1.5*paper_weight[1] * g/m**2
    top_weight = paper_weight[2] * g/m**2
    sheet_area = sheet_area.to(m**2)
    sheet_weight = [0,0,0]
    sheet_weight[0] = (sheet_area * backing_weight).to(kg)
    sheet_weight[1] = (sheet_area * fluting_weight).to(kg)
    sheet_weight[2] = (sheet_area * top_weight).to(kg)
    return sheet_weight

def printing_cost (sheet_size, number_of_sheets, is_printed = False):
    if not is_printed:
        return 0
    if number_of_sheets <= 1000:
        printing_cost = 1600 * INR / number_of_sheets
    elif number_of_sheets <= 2000:
        printing_cost = 2000 * INR / number_of_sheets
    elif number_of_sheets <= 3000:
        printing_cost = 2400 * INR / number_of_sheets
    elif number_of_sheets <= 4000:
        printing_cost = 2800 * INR / number_of_sheets
    elif number_of_sheets <= 5000:
        printing_cost = 3200 * INR / number_of_sheets
    elif number_of_sheets <= 6000:
        printing_cost = 3600 * INR / number_of_sheets
    elif number_of_sheets <= 7000:
        printing_cost = 4200 * INR / number_of_sheets
    elif number_of_sheets <= 8000:
        printing_cost = 4800 * INR / number_of_sheets
    elif number_of_sheets <= 9000:
        printing_cost = 5400 * INR / number_of_sheets
    elif number_of_sheets <= 10000:
        printing_cost = 6000 * INR / number_of_sheets
    else:
        printing_cost = 0.6 * INR
    return printing_cost

def lamination_cost (sheet_area, is_laminated = False):
    if not is_laminated:
        return 0
    sheet_area_inches = sheet_area.to(inch**2)
    lamination_cost = (sheet_area_inches/100) * 0.35 * INR / inch**2
    return lamination_cost

def corrugation_cost (sheet_weight, paper_quality):

    cost_corrugation = 8 * INR / kg
    cost_pasting_sheet = 2 * INR / kg
    cost_paper = 0
    for i in range(len(sheet_weight) - 1):
        cost_paper += sheet_weight[i] * (paper_quality[i].value + cost_corrugation + cost_pasting_sheet)  
    
    print(f"Cost of Liner: {cost_paper}")

    cost_paper += sheet_weight[2] * paper_quality[2].value
    print(f"Cost Top Paper: {sheet_weight[2] * paper_quality[2].value}")
    return cost_paper

def corrugation_cost_nf(sheet_weight, paper_quality):
    nf_corrugation_cost = 10 * INR / kg
    cost_paper = 0
    for i in range(len(sheet_weight) - 1):
        cost_paper += sheet_weight[i] * (paper_quality[i].value + nf_corrugation_cost)
    cost_paper += sheet_weight[2] * (paper_quality[2].value + nf_corrugation_cost)
    return cost_paper

def pasting_cost (sheet_area, ply_num, is_pasting):
    if (not is_pasting):
        return 0
    pasting_cost = (sheet_area * 1.5 * math.floor(ply_num/2) * INR/inch**2) / 1200
    return max(pasting_cost, 0.4 * INR)

def punching_cost (number_of_sheets, is_punching = True):
    if(not is_punching):
        return 0
    if number_of_sheets < 500:
        punching_cost = (500/number_of_boxes) * INR
    elif(number_of_sheets < 1000):
        punching_cost = 0.5 * INR
    elif(number_of_sheets < 3000):    
        punching_cost = 0.4 * INR
    else:
        punching_cost = 0.3 * INR
    return punching_cost

def sheet_manufacturing_cost (sheet_weight, paper_quality, sheet_area, number_of_sheets, ply_num, is_pasting, is_punching, is_laminated, is_printed, is_nf, is_scoring):
    if is_scoring:
        scoring_cost = 1 * INR
    else:
        scoring_cost = 0

    if is_nf:
        sheet_manufacturing_cost = corrugation_cost_nf(sheet_weight, paper_quality) + pasting_cost(sheet_area, ply_num, is_pasting) + scoring_cost + punching_cost(number_of_sheets, is_punching) + printing_cost(sheet_area, number_of_sheets, is_printed) + lamination_cost(sheet_area, is_laminated)
    else:
        sheet_manufacturing_cost = corrugation_cost(sheet_weight, paper_quality) + pasting_cost(sheet_area, ply_num, is_pasting) + punching_cost(number_of_sheets, is_punching) + printing_cost(sheet_area, number_of_sheets, is_printed) + lamination_cost(sheet_area, is_laminated) + scoring_cost

    sheet_manufacturing_cost = sheet_manufacturing_cost * 1.03 # 3% wastage
    
    return sheet_manufacturing_cost

def pinning_cost (number_of_pins):
    return number_of_pins * 0.15 * INR

def hand_pasting (length, is_hand_pasted = False):
    if not is_hand_pasted:
        return 0
    if length <= 10:
        hand_pasting_cost = 0.3 * INR
    elif length <= 20:
        hand_pasting_cost = 0.4 * INR
    elif length <= 30:
        hand_pasting_cost = 1 * INR 
    else:
        hand_pasting_cost = 2 * INR
    return hand_pasting_cost

def sales_price (cost):
    sales_price = [0, 0, 0, 0, 0, 0]

    for i in range(len(sales_price)):
        
        profit_margin = cost * 0.05 * (i + 1)
        
        sale_price = cost + profit_margin
        sales_price[i] = sale_price

    return sales_price

def bundling_cost (number_of_boxes):
    number_bundles = math.ceil(number_of_boxes / 100)


class PaperQuality_OG(Enum):
    Kraft = 37 * INR / kg
    Duplex = 48 * INR / kg
    Golden = 42 * INR / kg
    PrePrinted = 0 * INR / kg
    Golden180 = 42 * INR / kg
    KraftImported = 75 * INR / kg
    ITCWhite = 70 * INR / kg

class PaperQuality_Adjusted(Enum):
    Kraft = PaperQuality_OG.Kraft.value * 1.06
    Duplex = PaperQuality_OG.Duplex.value * 1.06
    Golden = PaperQuality_OG.Golden.value * 1.06
    PrePrinted = PaperQuality_OG.PrePrinted.value * 1.06
    Golden180 = PaperQuality_OG.Golden180.value * 1.06
    KraftImported = PaperQuality_OG.KraftImported.value * 1.06
    ITCWhite = PaperQuality_OG.ITCWhite.value * 1.06


################################################################################

###Inputs###

length = 30 # in inches
width = 27 # in inches

paper_weight = [100, 100, 150] # in g/m^2 [Bottom, Flute, Top]
paper_quality = [PaperQuality_Adjusted.Kraft, PaperQuality_Adjusted.Kraft, PaperQuality_Adjusted.Golden] #[Bottom, Flute, Top]
# paper_quality= [PaperQuality_OG.Golden, PaperQuality_OG.Kraft, PaperQuality_OG.Duplex] #[Bottom, Flute, Top]

ply_num = 3
box_per_sheet = 0.5
number_of_boxes = 2000
number_of_sheets = number_of_boxes/box_per_sheet

is_nf = True # True if NF, False if not

is_pasting = True # True if pasting, False if not

is_punching = False # True if punching, False if not
is_scoring = True # True if scoring, False if not

is_laminated = False # True if laminated, False if not
is_printed = False # True if printed, False if not

is_hand_pasted = False # True if hand pasted, False if not
pins_per_box = 6 # Number of pins per box

only_corrugation = False # True if only liner, False if not
first_time = False # True if first time, False if not
transportation_cost = 0 * INR # Total Transportation /cost 

###InputsEnd###

# get_inputs (length, width, paper_quality, ply_num)    

sheet_area = sheet_area_inches (length, width)
print(f"Sheet Size: {sheet_area}")

if only_corrugation:
    corrugation_cost = 7 * INR / kg
    backing_weight = paper_weight[0] * g/m**2
    fluting_weight = 1.5*paper_weight[1] * g/m**2
    top_weight  = paper_weight[2] * g/m**2
    sheet_area = sheet_area.to(m**2)
    sheet_weight = [0,0,0]
    sheet_weight[0] = (sheet_area * backing_weight).to(kg)
    sheet_weight[1] = (sheet_area * fluting_weight).to(kg)
    sheet_weight[2] = (sheet_area * top_weight).to(kg)  # No top weight for only corrugation
    total_sheet_weight = sheet_weight[0]+sheet_weight[1]+sheet_weight[2]
    # print(f"Total Sheet Weight: {total_sheet_weight}")
    sheet_manufacturing_cost = total_sheet_weight * corrugation_cost

    print(f"Sheet Manufacturing Cost: {sheet_manufacturing_cost}")

    sheet_manufacturing_cost = sheet_manufacturing_cost + pasting_cost(sheet_area, ply_num, is_pasting) + punching_cost(number_of_sheets, is_punching)
 
    print(f"Total Manufacturing Cost: {sheet_manufacturing_cost}")
    
    cost_per_box = sheet_manufacturing_cost / box_per_sheet

    cost_per_box = cost_per_box + pinning_cost(pins_per_box) + hand_pasting(length, is_hand_pasted)

    print(f"Cost per box: {cost_per_box}")
    sales_price = sales_price(cost_per_box)
    print(f"Sales Price")
    for i in range(len(sales_price)):
        print(f"Sales Price ({(i+1)*5}%): {sales_price[i]}")


else:
    sheet_weight = sheet_weight (sheet_area, paper_weight, ply_num)
    print(f"Sheet Weight: {sheet_weight}")
    total_sheet_weight = sheet_weight[0]+sheet_weight[1]+sheet_weight[2]
    print(f"Total Sheet Weight: {total_sheet_weight}")

    print(f"This box has ")
    if is_punching:
        print(f"Punching")
    if is_laminated:
        print(f"Lamination")
    if is_printed:
        print(f"Printing")
    if pins_per_box > 0:
        print(f"Pinning with {pins_per_box} pins")
        is_hand_pasted = False
    if is_hand_pasted:
        print(f"Hand Pasting")


    print(f"This box has {box_per_sheet} boxes per sheet of {ply_num} ply. Total number of sheets: {number_of_sheets}, hence number of boxes: {number_of_boxes}")


    sheet_manufacturing_cost = sheet_manufacturing_cost(sheet_weight, paper_quality, sheet_area, number_of_sheets, ply_num,is_pasting, is_punching, is_laminated, is_printed, is_nf, is_scoring)
    print(f"Sheet Manufacturing Cost: {sheet_manufacturing_cost}")
    print(f"Corrugation Cost: {corrugation_cost(sheet_weight, paper_quality)}")
    print(f"Pasting: {pasting_cost(sheet_area, ply_num, is_pasting)}")
    print(f"Printing Cost: {printing_cost(sheet_area, number_of_sheets, is_printed)}")
    print(f"Punching Cost: {punching_cost(number_of_sheets, is_punching)}")
    print(f"Lamination Cost: {lamination_cost(sheet_area, is_laminated)}")
    print(f"Hand Pasting Cost: {hand_pasting(length, is_hand_pasted)}")
    print(f"Pinning Cost: {pinning_cost(pins_per_box)}")

    cost_paper = 0
    for i in range(len(sheet_weight)):
        cost_paper += sheet_weight[i] * (paper_quality[i].value) 
     
    print(f"Cost of Paper: {cost_paper}")    
    manufacturing_cost = sheet_manufacturing_cost/box_per_sheet + pinning_cost(pins_per_box) + hand_pasting(length, is_hand_pasted) + (transportation_cost/number_of_boxes)
    print(f"Transport Cost per box: {transportation_cost/number_of_boxes}")
    print(f"Manufacturing Cost: {manufacturing_cost}")

    sales_price = sales_price (manufacturing_cost)
    print(f"Sales Price")
    for i in range(len(sales_price)):
        print(f"Sales Price ({(i+1)*5}%): {sales_price[i]}")
        print(f"With Legacy Tax Rate: {sales_price[i]*1.12}")
        print(f"With New Tax Rate: {sales_price[i]*1.05}")

    # print(f"Total Manufacturing Cost: {manufacturing_cost * number_of_boxes}")
    # for i in range(len(sales_price)):
    #     total_sales_price = sales_price[i] * number_of_boxes
    #     print(f"Total Sales Price ({(i+1)*5}%): {total_sales_price}")
