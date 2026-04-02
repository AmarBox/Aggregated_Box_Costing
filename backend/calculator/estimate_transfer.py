"""
Transfer processed rows from Raw_Work.xlsx into Estimates.xlsx.

Each row is placed into a sheet named after the customer. Transferred rows
are removed from Raw_Work.xlsx.

Usage (CLI):  python -m calculator.estimate_transfer Raw_Work.xlsx Estimates.xlsx
Usage (API):  transfer(raw_work_path, estimates_path) -> summary dict
"""

from datetime import datetime

import openpyxl
from openpyxl.utils import get_column_letter

# Raw_Work column indices (1-based)
RW_NAME       = 1
RW_GROUP      = 2
RW_DATE       = 3
RW_LENGTH     = 4
RW_WIDTH      = 5
RW_BOTTOM_W   = 6
RW_BOTTOM_Q   = 7
RW_FLUTE_W    = 8
RW_FLUTE_Q    = 9
RW_TOP_W      = 10
RW_TOP_Q      = 11
RW_PLY        = 12
RW_ORDER_TYPE = 13
RW_UPS        = 14
RW_NUM_BOXES  = 15
RW_PUNCHING   = 16
RW_PINS       = 17
RW_ITEM_NAME  = 18
RW_RATE       = 19
RW_TOTAL      = 20

# Estimates column indices (1-based)
EST_SR_NO     = 1
EST_DATE      = 2
EST_PROGRAM   = 3
EST_PLY       = 4
EST_RATE      = 5
EST_NUM_BOXES = 6
EST_TOTAL     = 7

HEADERS = ['Sr. No.', 'Date', 'Program', 'Ply', 'Rate', 'Number of Boxes', 'Total']


def _format_num(n):
    """Show as int if whole number, else as float."""
    if float(n) == int(float(n)):
        return str(int(float(n)))
    return str(float(n))


def _build_program(length, width, bottom_w, bottom_q, flute_w, flute_q,
                   top_w, top_q, punching, pins, order_type=None, item_name=None):
    """Build a human-readable program description string."""
    parts = []
    if item_name:
        parts.append(str(item_name).strip())
    parts.append(f"{_format_num(length)}x{_format_num(width)} = "
                 f"{bottom_w}({bottom_q}) + {flute_w}({flute_q}) + {top_w}({top_q})")
    prog = " | ".join(parts)
    if order_type and str(order_type).strip().upper() != 'ALL':
        prog += f" ; {order_type}"
    if str(punching).strip().upper() == 'Y':
        prog += " ; Punching"
    if pins and int(pins) > 0:
        prog += f" ; Pins = {int(pins)}"
    return prog


def _get_or_create_sheet(wb, name):
    """Return (worksheet, is_new). Creates sheet with headers if it doesn't exist."""
    if name in wb.sheetnames:
        return wb[name], False
    ws = wb.create_sheet(title=name)
    for col, header in enumerate(HEADERS, 1):
        ws.cell(row=1, column=col).value = header
    return ws, True


def _find_last_sr_no(ws):
    """Find the highest Sr. No. in the sheet."""
    last = 0
    for row in range(2, ws.max_row + 1):
        val = ws.cell(row=row, column=EST_SR_NO).value
        if isinstance(val, (int, float)):
            last = max(last, int(val))
    return last


def _remove_grand_total_row(ws):
    """Remove the Grand Total row if it exists."""
    for row in range(ws.max_row, 1, -1):
        for col in range(1, EST_TOTAL + 1):
            val = ws.cell(row=row, column=col).value
            if isinstance(val, str) and 'Grand Total' in val:
                ws.delete_rows(row)
                return


def _add_grand_total(ws):
    """Add a Grand Total row below the last data row with a SUM formula."""
    last_data_row = ws.max_row
    if last_data_row < 2:
        return
    total_row = last_data_row + 1
    col_letter = get_column_letter(EST_TOTAL)
    ws.cell(row=total_row, column=EST_NUM_BOXES).value = "Grand Total"
    ws.cell(row=total_row, column=EST_TOTAL).value = (
        f"=SUM({col_letter}2:{col_letter}{last_data_row})"
    )


def transfer(raw_work_path, estimates_path):
    """
    Transfer processed rows from Raw_Work into Estimates.

    Returns a summary dict with counts and per-row details.
    """
    rw_wb = openpyxl.load_workbook(raw_work_path)
    rw_ws = rw_wb.active

    est_wb = openpyxl.load_workbook(estimates_path)

    rows_to_process = []
    for row_num in range(2, rw_ws.max_row + 1):
        name = rw_ws.cell(row=row_num, column=RW_NAME).value
        if name is None:
            break
        rate = rw_ws.cell(row=row_num, column=RW_RATE).value
        total = rw_ws.cell(row=row_num, column=RW_TOTAL).value
        if rate is None or total is None:
            continue
        rows_to_process.append(row_num)

    if not rows_to_process:
        return {'transferred': 0, 'details': [], 'message': 'No rows to transfer (run process first).'}

    modified_sheets = set()
    details = []

    for row_num in rows_to_process:
        name       = str(rw_ws.cell(row=row_num, column=RW_NAME).value).strip()
        date_val   = rw_ws.cell(row=row_num, column=RW_DATE).value
        length     = float(rw_ws.cell(row=row_num, column=RW_LENGTH).value)
        width      = float(rw_ws.cell(row=row_num, column=RW_WIDTH).value)
        bottom_w   = int(rw_ws.cell(row=row_num, column=RW_BOTTOM_W).value)
        bottom_q   = str(rw_ws.cell(row=row_num, column=RW_BOTTOM_Q).value).strip()
        flute_w    = int(rw_ws.cell(row=row_num, column=RW_FLUTE_W).value)
        flute_q    = str(rw_ws.cell(row=row_num, column=RW_FLUTE_Q).value).strip()
        top_w      = int(rw_ws.cell(row=row_num, column=RW_TOP_W).value)
        top_q      = str(rw_ws.cell(row=row_num, column=RW_TOP_Q).value).strip()
        ply        = int(rw_ws.cell(row=row_num, column=RW_PLY).value)
        order_type     = rw_ws.cell(row=row_num, column=RW_ORDER_TYPE).value
        punching   = rw_ws.cell(row=row_num, column=RW_PUNCHING).value
        pins       = rw_ws.cell(row=row_num, column=RW_PINS).value or 0
        item_name  = rw_ws.cell(row=row_num, column=RW_ITEM_NAME).value
        rate       = rw_ws.cell(row=row_num, column=RW_RATE).value
        num_boxes  = int(rw_ws.cell(row=row_num, column=RW_NUM_BOXES).value)
        total      = rw_ws.cell(row=row_num, column=RW_TOTAL).value

        est_ws, _ = _get_or_create_sheet(est_wb, name)

        if name not in modified_sheets:
            _remove_grand_total_row(est_ws)
        modified_sheets.add(name)

        next_sr = _find_last_sr_no(est_ws) + 1
        program = _build_program(length, width, bottom_w, bottom_q,
                                 flute_w, flute_q, top_w, top_q, punching, pins,
                                 order_type=order_type, item_name=item_name)

        new_row = est_ws.max_row + 1
        # Strip time component from date, keep only the date part
        if isinstance(date_val, datetime):
            date_val = date_val.date()
        elif isinstance(date_val, str):
            for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y'):
                try:
                    date_val = datetime.strptime(date_val, fmt).date()
                    break
                except ValueError:
                    pass

        est_ws.cell(row=new_row, column=EST_SR_NO).value     = next_sr
        date_cell = est_ws.cell(row=new_row, column=EST_DATE)
        date_cell.value = date_val
        date_cell.number_format = 'DD/MM/YYYY'
        est_ws.cell(row=new_row, column=EST_PROGRAM).value   = program
        est_ws.cell(row=new_row, column=EST_PLY).value       = ply
        est_ws.cell(row=new_row, column=EST_RATE).value      = rate
        est_ws.cell(row=new_row, column=EST_NUM_BOXES).value = num_boxes
        est_ws.cell(row=new_row, column=EST_TOTAL).value     = total

        details.append({
            'row': row_num,
            'name': name,
            'sr_no': next_sr,
            'program': program,
            'rate': rate,
            'total': total,
        })

    for sheet_name in modified_sheets:
        _add_grand_total(est_wb[sheet_name])

    # Clean up empty default sheet
    if 'Sheet1' in est_wb.sheetnames and len(est_wb.sheetnames) > 1:
        s1 = est_wb['Sheet1']
        if s1.max_row <= 1 and s1.cell(row=1, column=1).value is None:
            est_wb.remove(s1)

    # Remove transferred rows from Raw_Work (reverse order)
    for row_num in reversed(rows_to_process):
        rw_ws.delete_rows(row_num)

    est_wb.save(estimates_path)
    rw_wb.save(raw_work_path)

    return {
        'transferred': len(rows_to_process),
        'details': details,
        'message': f"Transferred {len(rows_to_process)} rows.",
    }
