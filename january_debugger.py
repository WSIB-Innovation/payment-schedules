#!/usr/bin/env python3
"""
January Issue Debugger
Debug why January 1-6 cases are still failing despite having special handling
"""

from datetime import datetime
from payment_schedule_generator import Table109Generator
from rapid_test_framework import RapidTester

def debug_january_issues():
    """Debug January 1-6 failures in detail"""
    
    print("=== JANUARY FAILURE DEBUG ===\n")
    
    tester = RapidTester()
    ground_truth = tester.ground_truth
    
    # Focus on January failures
    january_issues = []
    
    for (year, month), month_data in ground_truth.items():
        if month != 1:  # Only January
            continue
            
        gen = Table109Generator(year)
        
        for day, actual_payment in month_data.items():
            if day > 6:  # Only days 1-6
                continue
                
            run_date = datetime(year, month, day)
            predicted_payment = gen.calculate_payment_date(run_date)
            error = abs(predicted_payment - actual_payment)
            
            if error > 5:  # Large errors only
                january_issues.append({
                    'date': f"{year}-{month:02d}-{day:02d}",
                    'day': day,
                    'predicted': predicted_payment,
                    'actual': actual_payment,
                    'error': error,
                    'year': year
                })
    
    print(f"📊 JANUARY LARGE ERRORS (>5 days): {len(january_issues)} cases")
    print("="*60)
    
    for issue in sorted(january_issues, key=lambda x: (x['year'], x['day'])):
        print(f"{issue['date']}: predicted {issue['predicted']}, actual {issue['actual']} (error: {issue['error']} days)")
    
    print(f"\n🔍 DETAILED ANALYSIS:")
    print("="*40)
    
    # Test the January handler directly
    print("Testing handle_january_1_3_precisely function:")
    for issue in january_issues:
        if issue['day'] <= 3:
            gen = Table109Generator(issue['year'])
            run_date = datetime(issue['year'], 1, issue['day'])
            jan_result = gen.handle_january_1_3_precisely(run_date)
            print(f"  {issue['date']}: Jan handler returns {jan_result}, actual is {issue['actual']}")
            
            # Also test what the base algorithm would return
            base_result = gen.simple_2_working_days_back(run_date)
            print(f"    Base algorithm: {base_result.day} (month: {base_result.month})")
    
    print(f"\n💡 INSIGHTS:")
    
    # Pattern analysis
    days_1_3_issues = [i for i in january_issues if i['day'] <= 3]
    days_4_6_issues = [i for i in january_issues if i['day'] > 3]
    
    print(f"  Days 1-3 issues: {len(days_1_3_issues)} (should be handled by current fix)")
    print(f"  Days 4-6 issues: {len(days_4_6_issues)} (not covered by current fix)")
    
    if days_1_3_issues:
        print(f"\n  Days 1-3 patterns:")
        for issue in days_1_3_issues:
            print(f"    Day {issue['day']}: pred {issue['predicted']} → should be {issue['actual']}")
    
    if days_4_6_issues:
        print(f"\n  Days 4-6 patterns:")
        for issue in days_4_6_issues:
            print(f"    Day {issue['day']}: pred {issue['predicted']} → should be {issue['actual']}")

if __name__ == "__main__":
    debug_january_issues()
