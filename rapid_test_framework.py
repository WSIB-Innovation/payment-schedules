#!/usr/bin/env python3
"""
Rapid Testing Framework for Payment Schedule Algorithms
Allows quick testing of different algorithm approaches with immediate feedback
"""

import re
import calendar
from datetime import datetime, timedelta
import os
from collections import defaultdict
import holidays


class RapidTester:
    def __init__(self):
        self.ground_truth = self.load_ground_truth()
        
    def load_ground_truth(self):
        """Load ALL available ground truth data"""
        data = {}
        # Load ALL available years (they all use table_109_{year}.txt format)
        for year in [2014, 2015, 2016, 2017, 2018, 2020, 2021, 2022, 2023, 2024, 2025, 2026]:
            gt_file = f"table_examples/table_109_{year}.txt"
            if os.path.exists(gt_file):
                print(f"Loading {gt_file}...")
                year_data = self.parse_payment_table(gt_file, year)
                data.update(year_data)
                print(f"  → Loaded {len([k for k in year_data.keys() if k[0] == year])*31:,} potential dates for {year}")
        
        print(f"Total ground truth data loaded: {len(data)} month-entries")
        return data
    
    def parse_payment_table(self, filepath, year):
        """Parse payment table file"""
        data = {}
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Split into months
        months = re.split(r'\n(\w+) - \d{4}\n', content)
        current_month = None
        
        for i, section in enumerate(months):
            if i == 0:
                continue
                
            if i % 2 == 1:  # Month name
                current_month = section.strip()
                month_num = self._get_month_number(current_month)
                if month_num:
                    data[(year, month_num)] = {}
            elif i % 2 == 0 and current_month:  # Month data
                month_num = self._get_month_number(current_month)
                if month_num:
                    self._parse_month_data(section, data[(year, month_num)])
        
        return data
    
    def _get_month_number(self, month_name):
        """Convert month name to number"""
        months = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        return months.get(month_name)
    
    def _parse_month_data(self, month_section, month_data):
        """Parse individual month section"""
        lines = month_section.strip().split('\n')
        
        for line in lines:
            matches = re.findall(r'(\d{2}) : (\d{2})\s+\d{2}', line)
            for run_day, payment_day in matches:
                month_data[int(run_day)] = int(payment_day)
    
    def test_algorithm(self, algorithm_func, test_cases=None):
        """Test an algorithm function against ground truth"""
        results = {
            'total': 0, 'perfect': 0, 'close_1': 0, 'close_2': 0, 'major_errors': 0,
            'by_period': defaultdict(lambda: {'total': 0, 'perfect': 0}),
            'errors': []
        }
        
        test_data = test_cases or self.ground_truth
        
        for (year, month), month_data in test_data.items():
            for day, gt_payment in month_data.items():
                run_date = datetime(year, month, day)
                
                try:
                    predicted_payment = algorithm_func(run_date)
                    
                    results['total'] += 1
                    diff = abs(predicted_payment - gt_payment)
                    
                    # Track by period
                    period = self._get_period(year, month, day)
                    results['by_period'][period]['total'] += 1
                    
                    if diff == 0:
                        results['perfect'] += 1
                        results['by_period'][period]['perfect'] += 1
                    elif diff == 1:
                        results['close_1'] += 1
                    elif diff == 2:
                        results['close_2'] += 1
                    elif diff > 5:
                        results['major_errors'] += 1
                        results['errors'].append({
                            'date': f"{year}-{month:02d}-{day:02d}",
                            'predicted': predicted_payment,
                            'ground_truth': gt_payment,
                            'diff': diff
                        })
                
                except Exception as e:
                    results['errors'].append({
                        'date': f"{year}-{month:02d}-{day:02d}",
                        'error': str(e)
                    })
        
        return results
    
    def _get_period(self, year, month, day):
        """Get period classification"""
        if month == 1 and day <= 3:
            return "January_1_3"
        elif month == 12 and day >= 23:
            return "Christmas_Period"
        elif month == 4 and 10 <= day <= 18:
            return "Easter_Period"
        else:
            return "Regular"
    
    def print_results(self, results, algorithm_name="Algorithm"):
        """Print test results in a concise format"""
        total = results['total']
        if total == 0:
            print("No test cases found!")
            return
            
        perfect_pct = results['perfect'] / total * 100
        practical_pct = (results['perfect'] + results['close_1']) / total * 100
        acceptable_pct = (results['perfect'] + results['close_1'] + results['close_2']) / total * 100
        
        print(f"\n=== {algorithm_name} Results ===")
        print(f"Perfect Matches: {results['perfect']:4d}/{total} ({perfect_pct:5.1f}%)")
        print(f"Practical (≤1): {results['perfect'] + results['close_1']:4d}/{total} ({practical_pct:5.1f}%)")  
        print(f"Acceptable (≤2): {results['perfect'] + results['close_1'] + results['close_2']:4d}/{total} ({acceptable_pct:5.1f}%)")
        print(f"Major Errors:    {results['major_errors']:4d}/{total} ({results['major_errors']/total*100:5.1f}%)")
        
        print(f"\nBy Period:")
        for period, data in results['by_period'].items():
            if data['total'] > 0:
                period_pct = data['perfect'] / data['total'] * 100
                print(f"  {period:15s}: {data['perfect']:3d}/{data['total']:3d} ({period_pct:5.1f}%)")
        
        if results['errors'] and len(results['errors']) <= 5:
            print(f"\nErrors:")
            for error in results['errors'][:5]:
                if 'error' in error:
                    print(f"  {error['date']}: {error['error']}")
                else:
                    print(f"  {error['date']}: pred={error['predicted']}, gt={error['ground_truth']}, diff={error['diff']}")


# Test different algorithm approaches
def simple_2_working_days(run_date):
    """Original simple 2 working days back"""
    ca_holidays = holidays.Canada(years=run_date.year)
    
    working_days_back = 0
    current_date = run_date
    
    while working_days_back < 2:
        current_date -= timedelta(days=1)
        if current_date.weekday() < 5 and current_date not in ca_holidays:
            working_days_back += 1
    
    return current_date.day


def simple_with_january_fix(run_date):
    """Simple algorithm with just January 1-3 fix"""
    # Handle January 1-3
    if run_date.month == 1 and run_date.day <= 3:
        ca_holidays = holidays.Canada(years=run_date.year)
        
        # Based on ground truth patterns, target specific December dates
        prev_year = run_date.year - 1
        
        if run_date.day == 1 or run_date.day == 2:
            # Try to find 2nd-to-last working day in December
            dec_31 = datetime(prev_year, 12, 31)
            current_date = dec_31
            working_days_found = 0
            target_working_days = 2
            
            while current_date.month == 12:
                if current_date.weekday() < 5 and current_date not in holidays.Canada(years=prev_year):
                    working_days_found += 1
                    if working_days_found == target_working_days:
                        return current_date.day
                current_date -= timedelta(days=1)
            
            return 29  # Fallback
        else:  # Jan 3
            # Based on analysis, Jan 3 often goes to Dec 30
            return 30
    
    # Use simple algorithm for everything else
    return simple_2_working_days(run_date)


def targeted_christmas_fix(run_date):
    """Test targeted Christmas period fix"""
    ca_holidays = holidays.Canada(years=run_date.year)
    
    # Christmas period handling based on discovered patterns
    if run_date.month == 12 and run_date.day >= 23:
        # Based on ground truth analysis:
        # 2017: Dec 23-26 all mapped to payment day 22
        # 2016: Dec 23-27 all mapped to payment day 23
        
        # Find the last working day before Dec 23
        dec_22 = datetime(run_date.year, 12, 22)
        current_date = dec_22
        
        while current_date.month == 12 and (current_date.weekday() >= 5 or current_date in ca_holidays):
            current_date -= timedelta(days=1)
        
        if current_date.month == 12:
            return current_date.day
        else:
            return 22  # Fallback
    
    # Use simple algorithm with January fix for everything else
    return simple_with_january_fix(run_date)


def main():
    tester = RapidTester()
    
    print("Rapid Testing Framework - Payment Schedule Algorithms")
    print("=" * 60)
    
    # Test 1: Original simple algorithm
    results1 = tester.test_algorithm(simple_2_working_days)
    tester.print_results(results1, "Simple 2-Working-Days")
    
    # Test 2: Simple with January fix
    results2 = tester.test_algorithm(simple_with_january_fix)
    tester.print_results(results2, "Simple + January Fix")
    
    # Test 3: With Christmas fix too
    results3 = tester.test_algorithm(targeted_christmas_fix)
    tester.print_results(results3, "Simple + Jan + Christmas Fix")
    
    # Quick comparison
    print(f"\n=== COMPARISON ===")
    print(f"                   Perfect  Practical  Acceptable")
    print(f"Simple:            {results1['perfect']/results1['total']*100:6.1f}%  {(results1['perfect'] + results1['close_1'])/results1['total']*100:8.1f}%  {(results1['perfect'] + results1['close_1'] + results1['close_2'])/results1['total']*100:9.1f}%")
    print(f"+ January Fix:     {results2['perfect']/results2['total']*100:6.1f}%  {(results2['perfect'] + results2['close_1'])/results2['total']*100:8.1f}%  {(results2['perfect'] + results2['close_1'] + results2['close_2'])/results2['total']*100:9.1f}%")
    print(f"+ Christmas Fix:   {results3['perfect']/results3['total']*100:6.1f}%  {(results3['perfect'] + results3['close_1'])/results3['total']*100:8.1f}%  {(results3['perfect'] + results3['close_1'] + results3['close_2'])/results3['total']*100:9.1f}%")


if __name__ == "__main__":
    main()
