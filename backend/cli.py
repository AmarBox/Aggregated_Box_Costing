#!/usr/bin/env python
"""
CLI entry point for batch processing Raw_Work.xlsx files.

Usage:
    python cli.py process Raw_Work.xlsx              # Calculate costs
    python cli.py transfer Raw_Work.xlsx Estimates.xlsx  # Transfer to estimates
    python cli.py all Raw_Work.xlsx Estimates.xlsx       # Process + transfer
"""

import sys
import os

# Ensure the backend package is importable
sys.path.insert(0, os.path.dirname(__file__))

from calculator.batch_processor import process_workbook
from calculator.estimate_transfer import transfer


def print_usage():
    print(__doc__)
    sys.exit(1)


def cmd_process(raw_work_path):
    if not os.path.exists(raw_work_path):
        print(f"Error: {raw_work_path} not found")
        sys.exit(1)

    print(f"Processing {raw_work_path}...")
    results = process_workbook(raw_work_path)

    for r in results:
        print(f"  Row {r['row']} | {r['name']} | Group {r['group']} | "
              f"Date: {r['date']} | Cost: {r['cost_per_box']} | "
              f"Rate: {r['rate']} | Total: {r['total']}")

    print(f"\nProcessed {len(results)} rows. Results saved to {raw_work_path}")


def cmd_transfer(raw_work_path, estimates_path):
    if not os.path.exists(raw_work_path):
        print(f"Error: {raw_work_path} not found")
        sys.exit(1)

    if not os.path.exists(estimates_path):
        import openpyxl
        wb = openpyxl.Workbook()
        wb.save(estimates_path)
        print(f"Created new {estimates_path}")

    print(f"Transferring from {raw_work_path} to {estimates_path}...")
    summary = transfer(raw_work_path, estimates_path)

    for d in summary['details']:
        print(f"  Row {d['row']} -> '{d['name']}' Sr.{d['sr_no']}: {d['program']}")

    print(f"\n{summary['message']}")


def main():
    if len(sys.argv) < 3:
        print_usage()

    command = sys.argv[1].lower()

    if command == 'process':
        cmd_process(sys.argv[2])

    elif command == 'transfer':
        if len(sys.argv) < 4:
            print("Error: transfer requires both Raw_Work.xlsx and Estimates.xlsx paths")
            print_usage()
        cmd_transfer(sys.argv[2], sys.argv[3])

    elif command == 'all':
        if len(sys.argv) < 4:
            print("Error: all requires both Raw_Work.xlsx and Estimates.xlsx paths")
            print_usage()
        cmd_process(sys.argv[2])
        print()
        cmd_transfer(sys.argv[2], sys.argv[3])

    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == '__main__':
    main()
