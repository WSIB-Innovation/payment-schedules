#!/usr/bin/env python3
"""
January Ground Truth Analyzer
Examine actual patterns in January ground truth to understand the correct logic
"""

from datetime import datetime
from rapid_test_framework import RapidTester

def analyze_january_ground_truth():
    """Analyze all January cases to understand correct patterns"""
    
    print("=== JANUARY GROUND TRUTH ANALYSIS ===\n")
    
    tester = RapidTester()
    ground_truth = tester.ground_truth
    
    # Collect all January data
    january_data = []
    
    for (year, month), month_data in ground_truth.items():
        if month != 1:
            continue
            
        for day, actual_payment in month_data.items():
            if day > 6:  # Focus on days 1-6
                continue
                
            january_data.append({
                'year': year,
                'day': day,
                'actual_payment': actual_payment,
                'date': f"{year}-01-{day:02d}"
            })
    
    # Sort by day then year
    january_data.sort(key=lambda x: (x['day'], x['year']))
    
    print(f"📊 ALL JANUARY 1-6 GROUND TRUTH DATA:")
    print("="*50)
    
    # Group by day
    by_day = {}
    for item in january_data:
        day = item['day']
        if day not in by_day:
            by_day[day] = []
        by_day[day].append(item)
    
    for day in sorted(by_day.keys()):
        cases = by_day[day]
        print(f"\nJANUARY {day} ({len(cases)} cases):")
        
        # Separate into December vs January payment dates
        december_payments = [c for c in cases if c['actual_payment'] > 25]
        january_payments = [c for c in cases if c['actual_payment'] <= 10]
        other_payments = [c for c in cases if 10 < c['actual_payment'] <= 25]
        
        if december_payments:
            print(f"  → DECEMBER PAYMENTS ({len(december_payments)}): ", end="")
            for c in december_payments:
                print(f"{c['year']}→{c['actual_payment']}", end=" ")
            print()
        
        if january_payments:
            print(f"  → JANUARY PAYMENTS ({len(january_payments)}): ", end="")
            for c in january_payments:
                print(f"{c['year']}→{c['actual_payment']}", end=" ")
            print()
        
        if other_payments:
            print(f"  → OTHER PAYMENTS ({len(other_payments)}): ", end="")
            for c in other_payments:
                print(f"{c['year']}→{c['actual_payment']}", end=" ")
            print()
    
    print(f"\n🔍 PATTERN ANALYSIS:")
    print("="*30)
    
    # Analyze patterns
    for day in sorted(by_day.keys()):
        cases = by_day[day]
        december_count = len([c for c in cases if c['actual_payment'] > 25])
        january_count = len([c for c in cases if c['actual_payment'] <= 10])
        
        total = len(cases)
        dec_pct = december_count / total * 100
        jan_pct = january_count / total * 100
        
        print(f"Jan {day}: {december_count}/{total} need December ({dec_pct:.0f}%), {january_count}/{total} need January ({jan_pct:.0f}%)")
        
        # Determine the predominant pattern
        if december_count > january_count:
            print(f"   → PRIMARY PATTERN: December payments")
        elif january_count > december_count:
            print(f"   → PRIMARY PATTERN: January payments")
        else:
            print(f"   → MIXED PATTERN: Need year-specific logic")
    
    print(f"\n💡 ALGORITHMIC INSIGHTS:")
    print("="*35)
    
    # Find years that consistently need December vs January
    december_years = set()
    january_years = set()
    
    for day in sorted(by_day.keys()):
        cases = by_day[day]
        for case in cases:
            if case['actual_payment'] > 25:
                december_years.add(case['year'])
            elif case['actual_payment'] <= 10:
                january_years.add(case['year'])
    
    print(f"Years that often need December payments: {sorted(december_years)}")
    print(f"Years that often need January payments: {sorted(january_years)}")
    
    # Check if there's a year-based pattern (like leap years, weekday patterns, etc.)
    print(f"\nYear analysis:")
    for year in sorted(set([c['year'] for c in january_data])):
        year_data = [c for c in january_data if c['year'] == year]
        dec_count = len([c for c in year_data if c['actual_payment'] > 25])
        jan_count = len([c for c in year_data if c['actual_payment'] <= 10])
        print(f"  {year}: {dec_count} Dec, {jan_count} Jan")

if __name__ == "__main__":
    analyze_january_ground_truth()
