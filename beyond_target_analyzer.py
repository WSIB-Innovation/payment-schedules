#!/usr/bin/env python3
"""
Beyond Target Analyzer
Analyze the remaining 172 cases with 3+ days offset to find fixable patterns
"""

from datetime import datetime
from collections import defaultdict, Counter
from payment_schedule_generator import Table109Generator
from rapid_test_framework import RapidTester
import calendar

def analyze_beyond_target_cases():
    """Deep analysis of 3+ day offset cases to find algorithmic fix opportunities"""
    
    print("=== BEYOND TARGET CASES ANALYSIS (3+ days offset) ===\n")
    
    tester = RapidTester()
    ground_truth = tester.ground_truth
    
    beyond_target_cases = []
    
    for (year, month), month_data in ground_truth.items():
        gen = Table109Generator(year)
        
        for day, actual_payment in month_data.items():
            run_date = datetime(year, month, day)
            predicted_payment = gen.calculate_payment_date(run_date)
            error = abs(predicted_payment - actual_payment)
            
            if error > 2:  # Beyond target cases only
                case_info = {
                    'date': f"{year}-{month:02d}-{day:02d}",
                    'year': year,
                    'month': month,
                    'day': day,
                    'weekday': run_date.strftime('%A'),
                    'predicted': predicted_payment,
                    'actual': actual_payment,
                    'error': error,
                    'direction': 'over' if predicted_payment > actual_payment else 'under',
                    'run_date_obj': run_date
                }
                beyond_target_cases.append(case_info)
    
    print(f"📊 TOTAL BEYOND TARGET CASES: {len(beyond_target_cases)}")
    print()
    
    # 1. MONTH PATTERNS
    print("🔍 1. MONTH PATTERNS:")
    month_groups = defaultdict(list)
    for case in beyond_target_cases:
        month_groups[case['month']].append(case)
    
    for month in sorted(month_groups.keys()):
        cases = month_groups[month]
        print(f"  Month {month:2d} ({calendar.month_name[month]:>9}): {len(cases):3d} cases")
    print()
    
    # 2. DAY OF MONTH PATTERNS
    print("🔍 2. DAY OF MONTH PATTERNS:")
    day_groups = defaultdict(list)
    for case in beyond_target_cases:
        day_groups[case['day']].append(case)
    
    # Show days with most problems
    day_counts = [(day, len(cases)) for day, cases in day_groups.items()]
    day_counts.sort(key=lambda x: x[1], reverse=True)
    
    print("  Most problematic days:")
    for day, count in day_counts[:10]:
        print(f"    Day {day:2d}: {count:3d} cases")
    print()
    
    # 3. WEEKDAY PATTERNS  
    print("🔍 3. WEEKDAY PATTERNS:")
    weekday_groups = defaultdict(list)
    for case in beyond_target_cases:
        weekday_groups[case['weekday']].append(case)
    
    for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if weekday in weekday_groups:
            cases = weekday_groups[weekday]
            print(f"  {weekday:>9}: {len(cases):3d} cases")
    print()
    
    # 4. ERROR DIRECTION AND MAGNITUDE
    print("🔍 4. ERROR PATTERNS:")
    direction_count = Counter([case['direction'] for case in beyond_target_cases])
    print(f"  Over-prediction (pred > actual): {direction_count['over']} cases")
    print(f"  Under-prediction (pred < actual): {direction_count['under']} cases")
    
    error_ranges = defaultdict(int)
    for case in beyond_target_cases:
        if case['error'] <= 5:
            error_ranges['3-5 days'] += 1
        elif case['error'] <= 10:
            error_ranges['6-10 days'] += 1
        elif case['error'] <= 20:
            error_ranges['11-20 days'] += 1
        else:
            error_ranges['21+ days (cross-month)'] += 1
    
    for range_name, count in error_ranges.items():
        print(f"  {range_name}: {count} cases")
    print()
    
    # 5. SPECIFIC ALGORITHMIC OPPORTUNITIES
    print("🎯 5. ALGORITHMIC FIX OPPORTUNITIES:")
    
    # Look for month-day combinations with multiple occurrences
    month_day_patterns = defaultdict(list)
    for case in beyond_target_cases:
        key = (case['month'], case['day'])
        month_day_patterns[key].append(case)
    
    recurring_patterns = {}
    for (month, day), cases in month_day_patterns.items():
        if len(cases) >= 3:  # Occurs in 3+ years - strong algorithmic pattern
            recurring_patterns[(month, day)] = cases
    
    if recurring_patterns:
        print(f"  Found {len(recurring_patterns)} recurring month-day patterns (3+ years):")
        for (month, day), cases in sorted(recurring_patterns.items()):
            years = [c['year'] for c in cases]
            errors = [c['error'] for c in cases]
            directions = [c['direction'] for c in cases]
            
            print(f"    {calendar.month_name[month]} {day}: {len(cases)} cases in years {years}")
            print(f"      Errors: {errors} days")  
            print(f"      Direction: {directions}")
            
            # Check if there's a consistent pattern
            if len(set(directions)) == 1:  # All same direction
                avg_error = sum(errors) / len(errors)
                direction = directions[0]
                print(f"      → CONSISTENT: Always {direction}-predicts by ~{avg_error:.1f} days")
            else:
                print(f"      → MIXED: Inconsistent direction")
        print()
    
    # 6. CROSS-MONTH BOUNDARY ISSUES STILL REMAINING
    large_errors = [case for case in beyond_target_cases if case['error'] > 20]
    if large_errors:
        print(f"🚨 6. REMAINING CROSS-MONTH ISSUES ({len(large_errors)} cases):")
        month_day_large = defaultdict(list)
        for case in large_errors:
            key = (case['month'], case['day'])
            month_day_large[key].append(case)
        
        for (month, day), cases in sorted(month_day_large.items()):
            print(f"    {calendar.month_name[month]} {day}: {len(cases)} cases")
            for case in cases:
                print(f"      {case['date']}: pred {case['predicted']} → actual {case['actual']} (error: {case['error']})")
    
    print(f"\n💡 IMPROVEMENT OPPORTUNITY:")
    fixable_patterns = len([cases for cases in recurring_patterns.values() if len(cases) >= 3])
    total_fixable_cases = sum([len(cases) for cases in recurring_patterns.values() if len(cases) >= 3])
    print(f"  Found {fixable_patterns} recurring patterns covering {total_fixable_cases} cases")
    print(f"  Fixing these could improve perfect accuracy by {total_fixable_cases/4135*100:.1f} percentage points")

if __name__ == "__main__":
    analyze_beyond_target_cases()
