#!/usr/bin/env python3
"""
Cross-Month Boundary Error Analyzer
Identify patterns in the remaining large errors (>10 days) to develop algorithmic fixes
"""

from datetime import datetime
from payment_schedule_generator import Table109Generator
from rapid_test_framework import RapidTester

def analyze_large_errors():
    """Analyze large errors (>10 days) to find algorithmic patterns"""
    
    print("=== CROSS-MONTH BOUNDARY ERROR ANALYSIS ===\n")
    
    tester = RapidTester()
    ground_truth = tester.ground_truth
    
    large_errors = []
    cross_month_errors = []
    
    for (year, month), month_data in ground_truth.items():
        gen = Table109Generator(year)
        
        for day, actual_payment in month_data.items():
            run_date = datetime(year, month, day)
            predicted_payment = gen.calculate_payment_date(run_date)
            error = abs(predicted_payment - actual_payment)
            
            if error > 10:  # Large errors only
                error_info = {
                    'date': f"{year}-{month:02d}-{day:02d}",
                    'run_date': (month, day),
                    'predicted': predicted_payment,
                    'actual': actual_payment,
                    'error': error,
                    'year': year,
                    'month': month,
                    'day': day
                }
                large_errors.append(error_info)
                
                # Check if it's a cross-month boundary error (>25 day error suggests month crossing)
                if error > 25:
                    cross_month_errors.append(error_info)
    
    print(f"📊 LARGE ERROR ANALYSIS:")
    print(f"Total large errors (>10 days): {len(large_errors)}")
    print(f"Cross-month boundary errors (>25 days): {len(cross_month_errors)}")
    print()
    
    # Analyze cross-month patterns
    if cross_month_errors:
        print("🔍 CROSS-MONTH BOUNDARY ERROR PATTERNS:")
        print("="*70)
        
        # Group by month-day combination
        patterns = {}
        for error in cross_month_errors:
            key = (error['month'], error['day'])
            if key not in patterns:
                patterns[key] = []
            patterns[key].append(error)
        
        # Show patterns that repeat across multiple years
        recurring_patterns = {}
        for (month, day), errors in patterns.items():
            if len(errors) >= 2:  # Occurs in multiple years
                recurring_patterns[(month, day)] = errors
        
        print(f"Recurring cross-month patterns (occur in ≥2 years): {len(recurring_patterns)}")
        print()
        
        for (month, day), errors in sorted(recurring_patterns.items()):
            years = [e['year'] for e in errors]
            error_types = set()
            for e in errors:
                if e['predicted'] > e['actual']:
                    error_types.add(f"pred:{e['predicted']} > act:{e['actual']} (overshoot)")
                else:
                    error_types.add(f"pred:{e['predicted']} < act:{e['actual']} (undershoot)")
            
            print(f"  {month:02d}-{day:02d}: {len(errors)} cases in years {years}")
            for error_type in error_types:
                print(f"    {error_type}")
        print()
        
        # Show individual large errors for January (most critical)
        print("🎯 JANUARY LARGE ERRORS (highest priority):")
        january_errors = [e for e in large_errors if e['month'] == 1]
        for error in sorted(january_errors, key=lambda x: x['day']):
            print(f"  {error['date']}: predicted {error['predicted']}, actual {error['actual']} (error: {error['error']} days)")
        print()
        
        # Show algorithmic insights
        print("💡 ALGORITHMIC INSIGHTS FOR FIXES:")
        print("="*50)
        
        # January pattern analysis
        jan_patterns = [e for e in cross_month_errors if e['month'] == 1]
        if jan_patterns:
            print("1. JANUARY 1-6 CROSS-MONTH PATTERN:")
            for error in sorted(jan_patterns, key=lambda x: x['day']):
                if error['predicted'] > error['actual']:
                    print(f"   Jan {error['day']}: Algorithm predicts {error['predicted']} (Dec {error['predicted']}), should be {error['actual']} (Jan {error['actual']})")
                    print(f"   → FIX: When Jan 1-6 crosses to Dec, return Jan day instead")
            print()
        
        # August pattern analysis  
        aug_patterns = [e for e in cross_month_errors if e['month'] == 8]
        if aug_patterns:
            print("2. AUGUST CROSS-MONTH PATTERN:")
            for error in sorted(aug_patterns, key=lambda x: x['day']):
                if error['predicted'] > error['actual']:
                    print(f"   Aug {error['day']}: Algorithm predicts {error['predicted']} (Jul {error['predicted']}), should be {error['actual']} (Aug {error['actual']})")
                    print(f"   → FIX: When Aug 1-4 crosses to Jul, return Aug day instead")
            print()
        
        # Other patterns
        other_patterns = [e for e in cross_month_errors if e['month'] not in [1, 8]]
        if other_patterns:
            print("3. OTHER CROSS-MONTH PATTERNS:")
            month_groups = {}
            for error in other_patterns:
                month = error['month']
                if month not in month_groups:
                    month_groups[month] = []
                month_groups[month].append(error)
            
            for month, errors in sorted(month_groups.items()):
                print(f"   Month {month}: {len(errors)} cases")
                for error in sorted(errors, key=lambda x: x['day']):
                    print(f"     Day {error['day']}: pred {error['predicted']} → should be {error['actual']}")
        
    print(f"\n📈 IMPROVEMENT OPPORTUNITY:")
    print(f"Fixing these {len(cross_month_errors)} cross-month errors could improve perfect accuracy by {len(cross_month_errors)/4135*100:.1f} percentage points")

if __name__ == "__main__":
    analyze_large_errors()