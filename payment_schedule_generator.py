#!/usr/bin/env python3
"""
Payment Schedule Generator - Table 109
Generates weekend/holiday payment tables based on business rules
"""

import argparse
import calendar
from datetime import datetime, timedelta
import holidays


class Table109Generator:
    def __init__(self, year):
        self.year = year
        self.canadian_holidays = holidays.Canada(years=year)
        
    def is_weekend(self, date):
        """Check if date is weekend (Saturday=5, Sunday=6)"""
        return date.weekday() >= 5
    
    def is_holiday(self, date):
        """Check if date is a statutory holiday"""
        return date in self.canadian_holidays
    
    def is_non_working_day(self, date):
        """Check if date is weekend or holiday"""
        return self.is_weekend(date) or self.is_holiday(date)
    
    def get_previous_working_day(self, date):
        """Get the previous working day (not weekend or holiday)"""
        current = date - timedelta(days=1)
        while self.is_non_working_day(current):
            current -= timedelta(days=1)
        return current
    
    def calculate_payment_date(self, run_date):
        """
        Calculate payment date based on business rules:
        - Look at run date and subtract 2 working days (not including run date)
        - For weekends: use same date as Friday
        - For holidays: use same as previous working day
        """
        
        # If run_date is weekend, find what Friday would have been
        if self.is_weekend(run_date):
            # Find the Friday of this week
            days_back_to_friday = run_date.weekday() - 4  # Friday is 4
            if days_back_to_friday < 0:
                days_back_to_friday += 7
            friday_date = run_date - timedelta(days=days_back_to_friday)
            return self.calculate_payment_date(friday_date)
        
        # If run_date is a holiday, use previous working day's value
        if self.is_holiday(run_date):
            prev_working_day = self.get_previous_working_day(run_date)
            return self.calculate_payment_date(prev_working_day)
        
        # Normal case: subtract 2 working days from run_date
        working_days_back = 0
        current_date = run_date
        
        while working_days_back < 2:
            current_date -= timedelta(days=1)
            if not self.is_non_working_day(current_date):
                working_days_back += 1
        
        return current_date.day
    
    def generate_month_table(self, month):
        """Generate Table 109 for a specific month"""
        month_name = calendar.month_name[month]
        days_in_month = calendar.monthrange(self.year, month)[1]
        
        print(f"\n{month_name} - {self.year}\n")
        print("                                                              ")
        print(" RUN   WKEND/HLDY     RUN  WKEND/HLDY        RUN  WKEND/HLDY  ")
        print(" DAY   FROM TO        DAY  FROM  TO          DAY  FROM TO     ")
        
        for day_group in range(0, 31, 3):  # Process in groups of 3
            line_parts = []
            
            for offset in range(3):
                day = day_group + offset + 1
                if day <= days_in_month:
                    run_date = datetime(self.year, month, day)
                    payment_day = self.calculate_payment_date(run_date)
                    line_parts.append(f"  {day:02d} : {payment_day:02d}   {payment_day:02d}")
                else:
                    if day <= 31:  # Show empty slots for days that don't exist in this month
                        line_parts.append(f"  {day:02d} :             ")
                    else:
                        line_parts.append("                ")
            
            print("     ".join(line_parts))
        
        print("                                                              ")
    
    def generate_year_table(self):
        """Generate Table 109 for the entire year"""
        print(f"Table - 109 - {self.year}")
        
        for month in range(1, 13):
            self.generate_month_table(month)


def parse_month(month_str):
    """Parse month from number or name (e.g., '3', 'Mar', 'MAR', 'March')"""
    if month_str.isdigit():
        month_num = int(month_str)
        if 1 <= month_num <= 12:
            return month_num
    else:
        # Try to parse month name/abbreviation
        month_str_lower = month_str.lower()
        month_names = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
        if month_str_lower in month_names:
            return month_names[month_str_lower]
    
    raise argparse.ArgumentTypeError(f"Invalid month: {month_str}. Use 1-12 or month name/abbreviation.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Payment Schedule Tables based on Business Rules",
        epilog="Examples:\n  %(prog)s --table 109 --year 2015\n  %(prog)s --table 109 --year 2015 --month 3\n  %(prog)s --table 109 --year 2015 --month Mar",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--table", 
        required=True,
        choices=["109"], 
        help="Table number to generate (currently supports 109)"
    )
    parser.add_argument(
        "--year", 
        required=True,
        type=int, 
        help="Year to generate table for"
    )
    parser.add_argument(
        "--month", 
        type=parse_month,
        help="Generate specific month only (1-12, or month name like 'Mar', 'March')"
    )
    
    args = parser.parse_args()
    
    if args.table == "109":
        generator = Table109Generator(args.year)
        
        if args.month:
            generator.generate_month_table(args.month)
        else:
            generator.generate_year_table()
    
    print("\n")  # Extra newline at end


if __name__ == "__main__":
    main() 