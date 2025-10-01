#!/usr/bin/env python3
"""
Algorithm Performance Tester
Tests the payment schedule algorithm against all historical data and provides comprehensive metrics.
"""

import os
import re
import calendar
from datetime import datetime
from collections import defaultdict
from payment_schedule_generator import Table109Generator


def load_all_historical_data():
    """Load all historical ground truth data from table_examples directory."""
    data = {}
    table_dir = "table_examples"
    
    if not os.path.exists(table_dir):
        print(f"❌ Error: {table_dir} directory not found")
        return {}
    
    # Load all available years
    for year in [2014, 2015, 2016, 2017, 2018, 2020, 2021, 2022, 2023, 2024, 2025, 2026]:
        file_path = f"{table_dir}/table_109_{year}.txt"
        if os.path.exists(file_path):
            print(f"Loading {file_path}...")
            year_data = parse_payment_table(file_path, year)
            data.update(year_data)
            print(f"  → Loaded {len([k for k in year_data.keys() if k[0] == year])*31:,} potential dates for {year}")
    
    print(f"Total ground truth data loaded: {len(data)} month-entries")
    return data


def parse_payment_table(filepath, year):
    """Parse payment table file and extract ground truth data."""
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
            current_month = get_month_number(section)
        else:  # Month data
            if current_month:
                month_data = parse_month_data(section)
                if month_data:
                    data[(year, current_month)] = month_data
    
    return data


def get_month_number(month_name):
    """Convert month name to number."""
    months = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
        'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    return months.get(month_name.strip())


def parse_month_data(month_section):
    """Parse individual month section and extract day->payment mappings."""
    data = {}
    lines = month_section.strip().split('\n')
    
    for line in lines:
        # Look for patterns like "  01 : 29   29     02 : 30   30     03 : 01   01"
        matches = re.findall(r'(\d{1,2})\s*:\s*(\d{1,2})\s+(\d{1,2})', line)
        for run_day, _, payment_day in matches:
            run_day = int(run_day)
            payment_day = int(payment_day)
            if 1 <= run_day <= 31 and 1 <= payment_day <= 31:
                data[run_day] = payment_day
    
    return data


def test_algorithm_performance():
    """Test algorithm performance against all historical data."""
    print("=" * 80)
    print("PAYMENT SCHEDULE ALGORITHM PERFORMANCE TEST")
    print("=" * 80)
    print()
    
    # Load ground truth data
    ground_truth = load_all_historical_data()
    if not ground_truth:
        print("❌ No ground truth data loaded. Cannot run tests.")
        return
    
    print()
    
    # Initialize counters
    total_cases = 0
    perfect_matches = 0
    one_day_errors = 0
    two_day_errors = 0
    beyond_target_errors = 0
    large_errors = []
    
    # Test each case
    for (year, month), month_data in ground_truth.items():
        generator = Table109Generator(year)
        
        for day, actual_payment in month_data.items():
            total_cases += 1
            run_date = datetime(year, month, day)
            predicted_payment = generator.calculate_payment_date(run_date)
            
            error = abs(predicted_payment - actual_payment)
            
            if error == 0:
                perfect_matches += 1
            elif error == 1:
                one_day_errors += 1
            elif error == 2:
                two_day_errors += 1
            else:
                beyond_target_errors += 1
                
            # Track large errors for analysis
            if error > 10:
                large_errors.append({
                    'date': f"{year}-{month:02d}-{day:02d}",
                    'predicted': predicted_payment,
                    'actual': actual_payment,
                    'error': error
                })
    
    # Calculate percentages
    perfect_pct = (perfect_matches / total_cases) * 100
    one_day_pct = (one_day_errors / total_cases) * 100
    two_day_pct = (two_day_errors / total_cases) * 100
    beyond_target_pct = (beyond_target_errors / total_cases) * 100
    within_target = perfect_matches + one_day_errors + two_day_errors
    within_target_pct = (within_target / total_cases) * 100
    
    # Display results
    print("🎯 ALGORITHM PERFORMANCE RESULTS")
    print("=" * 50)
    print(f"Total Test Cases: {total_cases:,}")
    print()
    
    print("📊 PREDICTION QUALITY BREAKDOWN:")
    print(f"  Perfect (0 days):     {perfect_matches:4,} ({perfect_pct:5.1f}%) ✅")
    print(f"  1-day offset:         {one_day_errors:4,} ({one_day_pct:5.1f}%) ✅") 
    print(f"  2-day offset:         {two_day_errors:4,} ({two_day_pct:5.1f}%) ✅")
    print(f"  Beyond target (3+ days): {beyond_target_errors:4,} ({beyond_target_pct:5.1f}%) ❌")
    print()
    
    print("🎯 TARGET ACHIEVEMENT (≤2 days offset):")
    print(f"  Within Target: {within_target:,}/{total_cases:,} ({within_target_pct:.1f}%)")
    print(f"  Beyond Target: {beyond_target_errors:,}/{total_cases:,} ({beyond_target_pct:.1f}%)")
    
    if within_target_pct >= 95:
        print("  🏆 EXCELLENT: Exceeds 95% target achievement!")
    elif within_target_pct >= 90:
        print("  ✅ GOOD: Meets 90%+ target achievement")
    else:
        print("  ⚠️  NEEDS IMPROVEMENT: Below 90% target")
    
    print()
    
    # Large errors analysis
    if large_errors:
        print(f"🚨 LARGE ERRORS (>10 days): {len(large_errors)} cases")
        print("  Worst offenders:")
        # Sort by error size and show top 5
        large_errors.sort(key=lambda x: x['error'], reverse=True)
        for error in large_errors[:5]:
            print(f"    {error['date']}: predicted {error['predicted']}, actual {error['actual']} (off by {error['error']} days)")
        if len(large_errors) > 5:
            print(f"    ... and {len(large_errors) - 5} more")
    else:
        print("✅ No large errors (>10 days)!")
    
    print()
    
    # Data coverage summary
    years = sorted(set([key[0] for key in ground_truth.keys()]))
    print(f"📊 DATA COVERAGE:")
    print(f"  Years tested: {years}")
    print(f"  Total test period: {len(years)} years ({years[0]}-{years[-1]})")
    
    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_algorithm_performance()
