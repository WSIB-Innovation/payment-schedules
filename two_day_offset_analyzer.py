#!/usr/bin/env python3
"""
2-Day Offset Analyzer
Analyze the 193 cases with exactly 2-day offset to find fixable algorithmic patterns
"""

from datetime import datetime
from collections import defaultdict, Counter
from payment_schedule_generator import Table109Generator
from rapid_test_framework import RapidTester
import calendar

def analyze_two_day_offset_cases():
    """Deep analysis of exactly 2-day offset cases to find algorithmic fix opportunities"""
    
    print("=== 2-DAY OFFSET CASES ANALYSIS ===\n")
    
    tester = RapidTester()
    ground_truth = tester.ground_truth
    
    two_day_cases = []
    
    for (year, month), month_data in ground_truth.items():
        gen = Table109Generator(year)
        
        for day, actual_payment in month_data.items():
            run_date = datetime(year, month, day)
            predicted_payment = gen.calculate_payment_date(run_date)
            error = abs(predicted_payment - actual_payment)
            
            if error == 2:  # Exactly 2-day offset cases only
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
                two_day_cases.append(case_info)
    
    print(f"📊 TOTAL 2-DAY OFFSET CASES: {len(two_day_cases)}")
    print()
    
    # 1. MONTH PATTERNS
    print("🔍 1. MONTH PATTERNS:")
    month_groups = defaultdict(list)
    for case in two_day_cases:
        month_groups[case['month']].append(case)
    
    for month in sorted(month_groups.keys()):
        cases = month_groups[month]
        print(f"  Month {month:2d} ({calendar.month_name[month]:>9}): {len(cases):3d} cases")
    print()
    
    # 2. DAY OF MONTH PATTERNS
    print("🔍 2. DAY OF MONTH PATTERNS:")
    day_groups = defaultdict(list)
    for case in two_day_cases:
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
    for case in two_day_cases:
        weekday_groups[case['weekday']].append(case)
    
    for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if weekday in weekday_groups:
            cases = weekday_groups[weekday]
            print(f"  {weekday:>9}: {len(cases):3d} cases")
    print()
    
    # 4. ERROR DIRECTION
    print("🔍 4. ERROR DIRECTION:")
    direction_count = Counter([case['direction'] for case in two_day_cases])
    print(f"  Over-prediction (pred > actual): {direction_count['over']} cases")
    print(f"  Under-prediction (pred < actual): {direction_count['under']} cases")
    print()
    
    # 5. SPECIFIC ALGORITHMIC OPPORTUNITIES - RECURRING PATTERNS
    print("🎯 5. ALGORITHMIC FIX OPPORTUNITIES:")
    
    # Look for month-day combinations with multiple occurrences across years
    month_day_patterns = defaultdict(list)
    for case in two_day_cases:
        key = (case['month'], case['day'])
        month_day_patterns[key].append(case)
    
    recurring_patterns = {}
    for (month, day), cases in month_day_patterns.items():
        if len(cases) >= 3:  # Occurs in 3+ years - strong algorithmic pattern
            recurring_patterns[(month, day)] = cases
    
    if recurring_patterns:
        print(f"  Found {len(recurring_patterns)} recurring month-day patterns (3+ years):")
        print()
        
        # Sort by frequency and consistency for prioritization
        pattern_scores = []
        for (month, day), cases in recurring_patterns.items():
            years = [c['year'] for c in cases]
            directions = [c['direction'] for c in cases]
            consistency = len(set(directions)) == 1  # All same direction
            frequency = len(cases)
            score = frequency * (2 if consistency else 1)  # Bonus for consistency
            
            pattern_scores.append({
                'month': month,
                'day': day,
                'cases': cases,
                'frequency': frequency,
                'consistency': consistency,
                'score': score,
                'years': years,
                'directions': directions
            })
        
        # Sort by score (highest first)
        pattern_scores.sort(key=lambda x: x['score'], reverse=True)
        
        print("  PRIORITIZED PATTERNS (by score):")
        print("  " + "="*70)
        
        for i, pattern in enumerate(pattern_scores[:15]):  # Top 15 patterns
            month_name = calendar.month_name[pattern['month']]
            print(f"  #{i+1:2d}. {month_name} {pattern['day']:2d}: {pattern['frequency']} cases in years {pattern['years']}")
            
            if pattern['consistency']:
                direction = pattern['directions'][0]
                print(f"       → CONSISTENT: Always {direction}-predicts by 2 days (Score: {pattern['score']:.1f})")
            else:
                print(f"       → MIXED: {pattern['directions']} (Score: {pattern['score']:.1f})")
            
            # Show specific examples
            for case in pattern['cases'][:3]:  # First 3 examples
                print(f"         {case['date']}: pred {case['predicted']} → actual {case['actual']} ({case['direction']})")
            if len(pattern['cases']) > 3:
                print(f"         ... and {len(pattern['cases'])-3} more")
            print()
    
    # 6. WEEKEND/WEEKDAY ANALYSIS FOR 2-DAY PATTERNS
    print("🔍 6. WEEKDAY-SPECIFIC PATTERNS:")
    print("  " + "="*40)
    
    for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if weekday in weekday_groups:
            cases = weekday_groups[weekday]
            over_count = len([c for c in cases if c['direction'] == 'over'])
            under_count = len([c for c in cases if c['direction'] == 'under'])
            
            print(f"  {weekday:>9} ({len(cases):3d} total): {over_count:3d} over, {under_count:3d} under")
            
            # Check if there's a strong bias
            if len(cases) >= 10:  # Only analyze weekdays with enough cases
                if over_count > under_count * 2:
                    print(f"    → PATTERN: {weekday}s tend to OVER-predict by 2 days")
                elif under_count > over_count * 2:
                    print(f"    → PATTERN: {weekday}s tend to UNDER-predict by 2 days")
    
    print(f"\n💡 IMPROVEMENT OPPORTUNITY:")
    total_fixable_cases = sum([len(cases) for cases in recurring_patterns.values()])
    perfect_improvement = total_fixable_cases / 4135 * 100
    print(f"  Found {len(recurring_patterns)} recurring patterns covering {total_fixable_cases} cases")
    print(f"  Converting these 2-day errors to perfect matches could improve perfect accuracy by {perfect_improvement:.1f} percentage points")
    print(f"  This would push perfect accuracy from 76.6% to ~{76.6 + perfect_improvement:.1f}%")
    
    return pattern_scores[:10] if recurring_patterns else []  # Return top 10 for implementation

if __name__ == "__main__":
    patterns = analyze_two_day_offset_cases()
