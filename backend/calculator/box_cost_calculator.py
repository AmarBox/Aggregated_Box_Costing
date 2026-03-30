from enum import Enum
from pint import UnitRegistry
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Initialize unit registry
ureg = UnitRegistry()
ureg.define('INR = [currency]')

# Define units
cm = ureg.cm
g = ureg.g
kg = ureg.kg
inch = ureg.inch
m = ureg.m
INR = ureg.INR


class BoxType(Enum):
    """Enum for different box types."""
    UNIVERSAL = "universal"
    BOTTOM_LOCKING = "bottom_locking"
    MOBILE_TYPE = "mobile_type"
    RING_FLAP = "ring_flap"


class PaperQuality(Enum):
    """Enum for different paper qualities with their default costs per kg."""
    KRAFT = 35.5
    DUPLEX = 45
    GOLDEN = 37.50
    PREPRINTED = 0
    GOLDEN180 = 44.5
    ITC = 70

    @classmethod
    def get_cost(cls, quality_name, cost_overrides=None):
        """Get cost per kg for a paper quality.

        Args:
            quality_name: Name of the paper quality (e.g. "KRAFT")
            cost_overrides: Optional dict of {quality_name: cost_per_kg} from monthly costs
        """
        if cost_overrides and quality_name in cost_overrides:
            return cost_overrides[quality_name] * INR / kg
        return cls[quality_name].value * INR / kg

    @classmethod
    def set_cost(cls, quality_name, new_cost):
        cls._member_map_[quality_name]._value_ = new_cost



@dataclass
class BoxDimensions:
    """Data class to hold box dimensions."""
    length: float
    width: float
    height: float
    units: str = "inch"
    
    def to_inches(self):
        """Convert dimensions to inches if they're not already."""
        if self.units == "cm":
            unit = cm
        elif self.units == "m":
            unit = m
        else:
            unit = inch
            
        length_inches = (self.length * unit).to(inch).magnitude
        width_inches = (self.width * unit).to(inch).magnitude
        height_inches = (self.height * unit).to(inch).magnitude
        
        return BoxDimensions(length_inches, width_inches, height_inches, "inch")


@dataclass
class ManufacturingOptions:
    """Data class to hold manufacturing options."""
    is_punching: bool = True
    is_scoring: bool = False
    is_laminated: bool = False
    is_printed: bool = False
    is_hand_pasted: bool = False
    is_nf: bool = False
    only_corrugation: bool = False
    labour_only: bool = False


@dataclass
class ProductionDetails:
    """Data class to hold production details."""
    ply_num: int = 3
    box_per_sheet: int = 1
    pins_per_box: int = 6
    number_of_boxes: int = 1000
    paper_weight: List[float] = None  # [bottom, flute, top] in g/m²
    paper_quality: List[PaperQuality] = None  # [bottom, flute, top]
    
    def __post_init__(self):
        if self.paper_weight is None:
            self.paper_weight = [100, 100, 0]
        if self.paper_quality is None:
            self.paper_quality = [PaperQuality.DUPLEX, PaperQuality.KRAFT, PaperQuality.PREPRINTED]


@dataclass
class CostBreakdown:
    """Data class to hold cost breakdown results."""
    sheet_area: float
    sheet_weight: List[float]
    manufacturing_cost_per_box: float
    total_manufacturing_cost: float
    sales_prices: List[float]
    total_sales_prices: List[float]
    cost_components: dict


class BoxCostCalculator:
    """Main class for calculating box manufacturing costs."""
    
    def __init__(self):
        pass
    
    def calculate_sheet_size_from_box(self, box_dims: BoxDimensions, box_type: BoxType) -> Tuple[float, float]:
        """Calculate sheet size from box dimensions."""
        # Convert to inches first
        dims = box_dims.to_inches()
        length = dims.length * inch
        width = dims.width * inch
        height = dims.height * inch
        
        if box_type == BoxType.UNIVERSAL:
            sheet_length = (height + width)
            sheet_width = 2 * (length + width) + 1 * inch
            
        elif box_type == BoxType.BOTTOM_LOCKING:
            sheet_length = height + 1.5 * width + 2 * inch
            sheet_width = 2 * (length + width) + 1 * inch
            
        elif box_type == BoxType.MOBILE_TYPE:
            sheet_length = 4 * height + length + 1 * inch
            sheet_width = 2 * (height + width) + height
            
        elif box_type == BoxType.RING_FLAP:
            sheet_length = max(2 * (height.magnitude + width.magnitude) + 2,
                             2 * width.magnitude + length.magnitude + 2) * inch
            sheet_width = height + length + 2.5 * inch
        
        # Round up to nearest inch
        sheet_length = math.ceil(sheet_length.magnitude)
        sheet_width = math.ceil(sheet_width.magnitude)
        
        return sheet_length, sheet_width
    
    def sheet_area_calculation(self, length: float, width: float) -> float:
        """Calculate sheet area in square inches."""
        sheet_length = length * inch
        sheet_width = width * inch
        return sheet_length * sheet_width
    
    def calculate_sheet_weight(self, sheet_area, paper_weight: List[float], ply_num: int) -> List[float]:
        """Calculate sheet weight components."""
        backing_weight = int((ply_num/2)) * paper_weight[0] * g/m**2
        fluting_weight = int((ply_num/2)) * 1.5 * paper_weight[1] * g/m**2
        top_weight = paper_weight[2] * g/m**2
        
        sheet_area_m2 = sheet_area.to(m**2)
        sheet_weight = [0, 0, 0]
        sheet_weight[0] = (sheet_area_m2 * backing_weight).to(kg)
        sheet_weight[1] = (sheet_area_m2 * fluting_weight).to(kg)
        sheet_weight[2] = (sheet_area_m2 * top_weight).to(kg)
        
        return sheet_weight
    
    def calculate_printing_cost(self, sheet_size, number_of_boxes: int, is_printed: bool = False) -> float:
        """Calculate printing cost."""
        if not is_printed:
            return 0 * INR
            
        if number_of_boxes <= 1000:
            return 1600 * INR / number_of_boxes
        elif number_of_boxes <= 2000:
            return 2000 * INR / number_of_boxes
        elif number_of_boxes <= 3000:
            return 2200 * INR / number_of_boxes
        elif number_of_boxes <= 4000:
            return 2800 * INR / number_of_boxes
        elif number_of_boxes <= 5000:
            return 3200 * INR / number_of_boxes
        elif number_of_boxes <= 6000:
            return 3600 * INR / number_of_boxes
        elif number_of_boxes <= 7000:
            return 4200 * INR / number_of_boxes
        elif number_of_boxes <= 8000:
            return 4800 * INR / number_of_boxes
        elif number_of_boxes <= 9000:
            return 5400 * INR / number_of_boxes
        elif number_of_boxes <= 10000:
            return 6000 * INR / number_of_boxes
        else:
            return 0.6 * INR
    
    def calculate_lamination_cost(self, sheet_area, is_laminated: bool = False) -> float:
        """Calculate lamination cost."""
        lamination_multiplier = 0.4 * INR / m**2
        if not is_laminated:
            return 0 * INR
        sheet_area_inches = sheet_area.to(inch**2)
        return (sheet_area_inches/100) *  lamination_multiplier
    
    def calculate_corrugation_cost(self, sheet_weight: List[float], paper_quality: List[PaperQuality], cost_overrides=None) -> float:
        """Calculate corrugation cost."""
        cost_corrugation = 8 * INR / kg
        cost_pasting_sheet = 2 * INR / kg
        cost_paper = 0 * INR

        for i in range(len(sheet_weight) - 1):
            cost_paper += sheet_weight[i] * (PaperQuality.get_cost(paper_quality[i].name, cost_overrides) + cost_corrugation + cost_pasting_sheet)

        cost_paper += sheet_weight[2] * PaperQuality.get_cost(paper_quality[2].name, cost_overrides)
        return cost_paper

    def calculate_corrugation_cost_nf(self, sheet_weight: List[float], paper_quality: List[PaperQuality], cost_overrides=None) -> float:
        """Calculate NF corrugation cost."""
        nf_corrugation_cost = 15 * INR / kg
        cost_paper = 0 * INR

        for i in range(len(sheet_weight) - 1):
            # Ensure all operands are Pint Quantities with compatible units
            cost_paper += sheet_weight[i] * PaperQuality.get_cost(paper_quality[i].name, cost_overrides)
            cost_paper += sheet_weight[i] * nf_corrugation_cost
        cost_paper += sheet_weight[2] * PaperQuality.get_cost(paper_quality[2].name, cost_overrides)
        cost_paper += sheet_weight[2] * nf_corrugation_cost
        return cost_paper
    
    def calculate_pasting_cost(self, sheet_area, ply_num: int) -> float:
        """Calculate pasting cost."""
        pasting_cost = (sheet_area * 1.5 * ply_num/2 * INR/inch**2) / 1200
        return max(pasting_cost, 0.4 * INR)
    
    def calculate_punching_cost(self, number_of_sheets: int, is_punching: bool = True) -> float:
        """Calculate punching cost."""
        if not is_punching:
            return 0 * INR
            
        if number_of_sheets < 500:
            return (500/number_of_sheets) * INR
        elif number_of_sheets < 1000:
            return 0.5 * INR
        elif number_of_sheets < 3000:
            return 0.4 * INR
        else:
            return 0.3 * INR
    
    def calculate_pinning_cost(self, number_of_pins: int) -> float:
        """Calculate pinning cost."""
        return number_of_pins * 0.1 * INR
    
    def calculate_hand_pasting_cost(self, length: float, is_hand_pasted: bool = False) -> float:
        """Calculate hand pasting cost."""
        if not is_hand_pasted:
            return 0 * INR
            
        if length <= 10:
            return 0.3 * INR
        elif length <= 20:
            return 0.4 * INR
        elif length <= 30:
            return 1 * INR
        else:
            return 2 * INR
    
    def calculate_sales_prices(self, cost: float) -> List[float]:
        """Calculate sales prices with different profit margins."""
        sales_prices = []
        for i in range(6):
            profit_margin = cost * 0.05 * (i + 1)
            sale_price = cost + profit_margin
            sales_prices.append(sale_price)
        return sales_prices
    
    def calculate_total_cost(self,
                           sheet_length: float = None,
                           sheet_width: float = None,
                           box_dims: BoxDimensions = None,
                           box_type: BoxType = None,
                           production_details: ProductionDetails = None,
                           manufacturing_options: ManufacturingOptions = None,
                           cost_overrides: dict = None) -> CostBreakdown:
        """
        Main method to calculate total cost.

        Args:
            sheet_length: Direct sheet length input (bypasses box calculation)
            sheet_width: Direct sheet width input (bypasses box calculation)
            box_dims: Box dimensions (if calculating from box)
            box_type: Type of box (if calculating from box)
            production_details: Production specifications
            manufacturing_options: Manufacturing options
            cost_overrides: Optional dict of {quality_name: cost_per_kg} for date-based pricing

        Returns:
            CostBreakdown: Complete cost breakdown
        """
        if production_details is None:
            production_details = ProductionDetails()
        if manufacturing_options is None:
            manufacturing_options = ManufacturingOptions()
        
        # Validate ply number
        if production_details.ply_num % 2 == 0:
            raise ValueError("Ply number must be odd")
        
        # Calculate sheet dimensions
        if sheet_length is None or sheet_width is None:
            if box_dims is None or box_type is None:
                raise ValueError("Either provide sheet dimensions or box dimensions with box type")
            sheet_length, sheet_width = self.calculate_sheet_size_from_box(box_dims, box_type)
        
        # Calculate sheet area
        sheet_area = self.sheet_area_calculation(sheet_length, sheet_width)
        
        # Calculate number of sheets
        number_of_sheets = production_details.number_of_boxes / production_details.box_per_sheet
        
        # Handle labour-only case (no corrugation, no paper — only punching, pasting, pins, hand pasting, scoring)
        if manufacturing_options.labour_only:
            sheet_weight = self.calculate_sheet_weight(sheet_area, production_details.paper_weight, production_details.ply_num)
            number_of_sheets = production_details.number_of_boxes / production_details.box_per_sheet

            pasting_cost = self.calculate_pasting_cost(sheet_area, production_details.ply_num)
            punching_cost = self.calculate_punching_cost(number_of_sheets, manufacturing_options.is_punching)
            pinning_cost = self.calculate_pinning_cost(production_details.pins_per_box)
            hand_pasting_cost = self.calculate_hand_pasting_cost(sheet_length, manufacturing_options.is_hand_pasted)
            scoring_cost = 1 * INR if manufacturing_options.is_scoring else 0 * INR

            sheet_labour_cost = (pasting_cost + punching_cost + scoring_cost) * 1.02  # 2% wastage
            manufacturing_cost_per_box = sheet_labour_cost / production_details.box_per_sheet + pinning_cost + hand_pasting_cost

            sales_prices = self.calculate_sales_prices(manufacturing_cost_per_box)
            total_manufacturing_cost = manufacturing_cost_per_box * production_details.number_of_boxes
            total_sales_prices = [price * production_details.number_of_boxes for price in sales_prices]

            cost_components = {
                "pasting": pasting_cost.magnitude,
                "punching": punching_cost.magnitude,
                "pinning": pinning_cost.magnitude,
                "hand_pasting": hand_pasting_cost.magnitude,
                "scoring": scoring_cost.magnitude,
            }

            return CostBreakdown(
                sheet_area=sheet_area.magnitude,
                sheet_weight=[w.magnitude for w in sheet_weight],
                manufacturing_cost_per_box=manufacturing_cost_per_box.magnitude,
                total_manufacturing_cost=total_manufacturing_cost.magnitude,
                sales_prices=[p.magnitude for p in sales_prices],
                total_sales_prices=[p.magnitude for p in total_sales_prices],
                cost_components=cost_components,
            )

        # Handle only corrugation case (corrugation processing fee, no paper cost)
        if manufacturing_options.only_corrugation:
            sheet_weight = self.calculate_sheet_weight(sheet_area, production_details.paper_weight, production_details.ply_num)
            total_sheet_weight = sum(sheet_weight)
            number_of_sheets = production_details.number_of_boxes / production_details.box_per_sheet

            # Use NF corrugation rate if is_nf, else standard rate
            if manufacturing_options.is_nf:
                corrugation_rate = 15 * INR / kg
            else:
                corrugation_rate = 8 * INR / kg
            corrugation_cost = total_sheet_weight * corrugation_rate

            pasting_cost = self.calculate_pasting_cost(sheet_area, production_details.ply_num)
            punching_cost = self.calculate_punching_cost(number_of_sheets, manufacturing_options.is_punching)
            pinning_cost = self.calculate_pinning_cost(production_details.pins_per_box)
            hand_pasting_cost = self.calculate_hand_pasting_cost(sheet_length, manufacturing_options.is_hand_pasted)
            scoring_cost = 1 * INR if manufacturing_options.is_scoring else 0 * INR

            sheet_manufacturing_cost = (corrugation_cost + pasting_cost + punching_cost + scoring_cost) * 1.02  # 2% wastage
            manufacturing_cost_per_box = sheet_manufacturing_cost / production_details.box_per_sheet + pinning_cost + hand_pasting_cost

            sales_prices = self.calculate_sales_prices(manufacturing_cost_per_box)
            total_manufacturing_cost = manufacturing_cost_per_box * production_details.number_of_boxes
            total_sales_prices = [price * production_details.number_of_boxes for price in sales_prices]

            cost_components = {
                "corrugation": corrugation_cost.magnitude,
                "pasting": pasting_cost.magnitude,
                "punching": punching_cost.magnitude,
                "pinning": pinning_cost.magnitude,
                "hand_pasting": hand_pasting_cost.magnitude,
                "scoring": scoring_cost.magnitude,
            }

            return CostBreakdown(
                sheet_area=sheet_area.magnitude,
                sheet_weight=[w.magnitude for w in sheet_weight],
                manufacturing_cost_per_box=manufacturing_cost_per_box.magnitude,
                total_manufacturing_cost=total_manufacturing_cost.magnitude,
                sales_prices=[p.magnitude for p in sales_prices],
                total_sales_prices=[p.magnitude for p in total_sales_prices],
                cost_components=cost_components,
            )
        
        # Calculate sheet weight
        sheet_weight = self.calculate_sheet_weight(sheet_area, production_details.paper_weight, production_details.ply_num)
        
        # Calculate cost components
        scoring_cost = 0 * INR
        if manufacturing_options.is_nf or (not manufacturing_options.is_punching and manufacturing_options.is_scoring):
            scoring_cost = 1 * INR
        
        if manufacturing_options.is_nf:
            corrugation_cost = self.calculate_corrugation_cost_nf(sheet_weight, production_details.paper_quality, cost_overrides)
        else:
            corrugation_cost = self.calculate_corrugation_cost(sheet_weight, production_details.paper_quality, cost_overrides)
        
        pasting_cost = self.calculate_pasting_cost(sheet_area, production_details.ply_num)
        punching_cost = self.calculate_punching_cost(number_of_sheets, manufacturing_options.is_punching)
        printing_cost = self.calculate_printing_cost(sheet_area, production_details.number_of_boxes, manufacturing_options.is_printed)
        lamination_cost = self.calculate_lamination_cost(sheet_area, manufacturing_options.is_laminated)
        pinning_cost = self.calculate_pinning_cost(production_details.pins_per_box)
        hand_pasting_cost = self.calculate_hand_pasting_cost(sheet_length, manufacturing_options.is_hand_pasted)
        
        # Calculate sheet manufacturing cost
        sheet_manufacturing_cost = corrugation_cost + pasting_cost + scoring_cost
        if not manufacturing_options.is_nf:
            sheet_manufacturing_cost += punching_cost + printing_cost + lamination_cost
        
        # Add 2% wastage
        sheet_manufacturing_cost = sheet_manufacturing_cost * 1.02
        
        # Calculate per box cost
        manufacturing_cost_per_box = (sheet_manufacturing_cost / production_details.box_per_sheet + 
                                    pinning_cost + hand_pasting_cost)
        
        # Calculate sales prices
        sales_prices = self.calculate_sales_prices(manufacturing_cost_per_box)
        
        # Calculate totals
        total_manufacturing_cost = manufacturing_cost_per_box * production_details.number_of_boxes
        total_sales_prices = [price * production_details.number_of_boxes for price in sales_prices]
        
        # Cost breakdown
        cost_components = {
            "corrugation": corrugation_cost.magnitude,
            "pasting": pasting_cost.magnitude,
            "punching": punching_cost.magnitude,
            "printing": printing_cost.magnitude,
            "lamination": lamination_cost.magnitude,
            "scoring": scoring_cost.magnitude,
            "pinning": pinning_cost.magnitude,
            "hand_pasting": hand_pasting_cost.magnitude,
            "sheet_manufacturing": sheet_manufacturing_cost.magnitude
        }
        
        return CostBreakdown(
            sheet_area=sheet_area.magnitude,
            sheet_weight=[w.magnitude for w in sheet_weight],
            manufacturing_cost_per_box=manufacturing_cost_per_box.magnitude,
            total_manufacturing_cost=total_manufacturing_cost.magnitude,
            sales_prices=[p.magnitude for p in sales_prices],
            total_sales_prices=[p.magnitude for p in total_sales_prices],
            cost_components=cost_components
        )


# Example usage and testing
if __name__ == "__main__":
    calculator = BoxCostCalculator()
    
    # Example 1: Calculate from box dimensions
    print("=== Example 1: Calculate from Box Dimensions ===")
    box_dims = BoxDimensions(length=23, width=17, height=6, units="cm")
    production_details = ProductionDetails(
        ply_num=3,
        number_of_boxes=3300,
        paper_weight=[100, 100, 150],
        paper_quality=[PaperQuality.KRAFT, PaperQuality.KRAFT, PaperQuality.GOLDEN]
    )
    manufacturing_options = ManufacturingOptions(
        is_punching=True,
        is_printed=False,
        is_laminated=False
    )
    
    result = calculator.calculate_total_cost(
        box_dims=box_dims,
        box_type=BoxType.UNIVERSAL,
        production_details=production_details,
        manufacturing_options=manufacturing_options
    )
    
    print(f"Sheet Area: {result.sheet_area:.2f} sq inches")
    print(f"Manufacturing Cost per Box: {result.manufacturing_cost_per_box:.2f} INR")
    print(f"Total Manufacturing Cost: {result.total_manufacturing_cost:.2f} INR")
    print(f"Sales Prices (5%-30%): {[f'{p:.2f}' for p in result.sales_prices]}")
    
    print("\n=== Example 2: Direct Sheet Size Input ===")
    # Example 2: Direct sheet size input
    result2 = calculator.calculate_total_cost(
        sheet_length=22,
        sheet_width=10.5,
        production_details=production_details,
        manufacturing_options=manufacturing_options
    )
    
    print(f"Sheet Area: {result2.sheet_area:.2f} sq inches")
    print(f"Manufacturing Cost per Box: {result2.manufacturing_cost_per_box:.2f} INR")
    print(f"Total Manufacturing Cost: {result2.total_manufacturing_cost:.2f} INR")