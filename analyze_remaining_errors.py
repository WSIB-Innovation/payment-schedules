#!/usr/bin/env python3
"""
Analyze the remaining 22% of cases where we don't achieve perfect accuracy
Identify patterns in failures to understand what's blocking 100% accuracy
"""

from rapid_test_framework import RapidTester
from payment_schedule_generator import Table109Generator
from datetime import datetime
import holidays
from collections import defaultdict, Counter


def optimized_algorithm(run_date):
    """Optimized algorithm wrapper"""  
    generator = Table109Generator(run_date.year)
    return generator.calculate_payment_date(run_date)


def analyze_failure_patterns():
    """Deep dive into what's causing the remaining failures"""
    tester = RapidTester()
    
    print("DEEP DIVE: ANALYZING THE REMAINING 22% ACCURACY GAP")
    print("=" * 60)
    
    # Get detailed results
    results = tester.test_algorithm(optimized_algorithm)
    
    # Collect all failures (non-perfect matches)
    failures = []
    successes = []
    
    for (year, month), month_data in tester.ground_truth.items():
        ca_holidays = holidays.Canada(years=year)
        
        for day, gt_payment in month_data.items():
            run_date = datetime(year, month, day)
            
            try:
                predicted_payment = optimized_algorithm(run_date)
                diff = abs(predicted_payment - gt_payment)
                
                failure_info = {
                    'date': run_date,
                    'year': year,
                    'month': month,
                    'day': day,
                    'weekday': run_date.strftime('%A'),
                    'predicted': predicted_payment,
                    'ground_truth': gt_payment,
                    'difference': diff,
                    'is_holiday': run_date in ca_holidays,
                    'is_weekend': run_date.weekday() >= 5,
                    'period': get_period_context(year, month, day)
                }
                
                if diff == 0:
                    successes.append(failure_info)
                else:
                    failures.append(failure_info)
                    
            except Exception as e:
                print(f"Error processing {year}-{month:02d}-{day:02d}: {e}")
    
    print(f"Total cases: {len(successes) + len(failures)}")
    print(f"Perfect matches: {len(successes)} ({len(successes)/(len(successes) + len(failures))*100:.1f}%)")
    print(f"Failures to analyze: {len(failures)} ({len(failures)/(len(successes) + len(failures))*100:.1f}%)")
    
    # Analyze failure patterns
    analyze_failure_patterns_detailed(failures)
    
    # Find the most problematic specific cases
    find_worst_failures(failures)
    
    # Look for sequential patterns
    analyze_sequential_patterns(failures)
    
    # Generate actionable insights
    generate_insights_for_manual_team(failures)


def get_period_context(year, month, day):
    """Get detailed period context"""
    if month == 1 and day <= 3:
        return f"January_1_3"
    elif month == 12 and day >= 23:
        return f"Christmas_Period"
    elif month == 4 and 10 <= day <= 18:
        return f"Easter_Period"
    elif month == 12 and day >= 15:
        return f"December_Late"
    elif month == 1 and day <= 10:
        return f"January_Early"
    elif day <= 5:
        return f"Month_Start"
    elif day >= 25:
        return f"Month_End"
    else:
        return f"Regular"


def analyze_failure_patterns_detailed(failures):
    """Analyze patterns in the failures"""
    print(f"\n{'='*60}")
    print(f"FAILURE PATTERN ANALYSIS")
    print(f"{'='*60}")
    
    # Group by difference size
    diff_counter = Counter([f['difference'] for f in failures])
    print(f"\nFailure by difference size:")
    for diff, count in sorted(diff_counter.items()):
        print(f"  {diff:2d} days off: {count:3d} cases ({count/len(failures)*100:5.1f}%)")
    
    # Group by period
    period_failures = defaultdict(list)
    for failure in failures:
        period_failures[failure['period']].append(failure)
    
    print(f"\nFailures by period:")
    for period, period_failures_list in sorted(period_failures.items(), key=lambda x: len(x[1]), reverse=True):
        avg_diff = sum(f['difference'] for f in period_failures_list) / len(period_failures_list)
        print(f"  {period:15s}: {len(period_failures_list):3d} cases (avg {avg_diff:.1f} days off)")
    
    # Group by weekday
    weekday_failures = defaultdict(list)
    for failure in failures:
        weekday_failures[failure['weekday']].append(failure)
    
    print(f"\nFailures by weekday:")
    for weekday in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if weekday in weekday_failures:
            failures_list = weekday_failures[weekday]
            avg_diff = sum(f['difference'] for f in failures_list) / len(failures_list)
            print(f"  {weekday:9s}: {len(failures_list):3d} cases (avg {avg_diff:.1f} days off)")
    
    # Group by month
    month_failures = defaultdict(list)
    for failure in failures:
        month_failures[failure['month']].append(failure)
    
    print(f"\nFailures by month:")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for i, month_name in enumerate(months, 1):
        if i in month_failures:
            failures_list = month_failures[i]
            avg_diff = sum(f['difference'] for f in failures_list) / len(failures_list)
            print(f"  {month_name}: {len(failures_list):3d} cases (avg {avg_diff:.1f} days off)")


def find_worst_failures(failures):
    """Find the worst individual failures"""
    print(f"\n{'='*60}")
    print(f"WORST INDIVIDUAL FAILURES (for manual review)")
    print(f"{'='*60}")
    
    # Sort by difference, then by frequency of similar patterns
    worst_failures = sorted(failures, key=lambda x: x['difference'], reverse=True)[:15]
    
    print(f"{'Date':<12} {'Day':<9} {'Pred':<4} {'GT':<4} {'Diff':<4} {'Period':<15} {'Notes'}")
    print(f"{'-'*12} {'-'*9} {'-'*4} {'-'*4} {'-'*4} {'-'*15} {'-'*20}")
    
    for failure in worst_failures:
        notes = []
        if failure['is_holiday']:
            notes.append("HOLIDAY")
        if failure['is_weekend']:
            notes.append("WEEKEND")
        
        date_str = f"{failure['year']}-{failure['month']:02d}-{failure['day']:02d}"
        print(f"{date_str:<12} {failure['weekday']:<9} {failure['predicted']:4d} {failure['ground_truth']:4d} {failure['difference']:4d} {failure['period']:<15} {' '.join(notes)}")


def analyze_sequential_patterns(failures):
    """Look for patterns in sequential dates"""
    print(f"\n{'='*60}")
    print(f"SEQUENTIAL PATTERN ANALYSIS")
    print(f"{'='*60}")
    
    # Group failures by month-year
    monthly_failures = defaultdict(list)
    for failure in failures:
        key = (failure['year'], failure['month'])
        monthly_failures[key].append(failure)
    
    print(f"Months with high failure rates:")
    for (year, month), failures_list in sorted(monthly_failures.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        if len(failures_list) >= 5:  # Only show months with significant failures
            avg_diff = sum(f['difference'] for f in failures_list) / len(failures_list)
            print(f"  {year}-{month:02d}: {len(failures_list):2d} failures (avg {avg_diff:.1f} days off)")
            
            # Look for consecutive day patterns
            consecutive_groups = find_consecutive_failures(failures_list)
            for group in consecutive_groups:
                if len(group) >= 2:
                    days_str = f"{group[0]['day']}-{group[-1]['day']}"
                    print(f"    Consecutive: days {days_str} ({len(group)} days in a row)")


def find_consecutive_failures(failures_list):
    """Find consecutive day failure patterns"""
    failures_list.sort(key=lambda x: x['day'])
    
    consecutive_groups = []
    current_group = []
    
    for failure in failures_list:
        if not current_group or failure['day'] == current_group[-1]['day'] + 1:
            current_group.append(failure)
        else:
            if len(current_group) >= 2:
                consecutive_groups.append(current_group)
            current_group = [failure]
    
    if len(current_group) >= 2:
        consecutive_groups.append(current_group)
    
    return consecutive_groups


def generate_insights_for_manual_team(failures):
    """Generate actionable insights for tomorrow's call"""
    print(f"\n{'='*60}")
    print(f"KEY QUESTIONS FOR TOMORROW'S CALL WITH MANUAL TEAM")
    print(f"{'='*60}")
    
    # Find most common failure patterns
    period_failures = defaultdict(list)
    for failure in failures:
        period_failures[failure['period']].append(failure)
    
    biggest_problem_areas = sorted(period_failures.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    
    print(f"\n🔍 PRIORITY PROBLEM AREAS TO DISCUSS:")
    for i, (period, failures_list) in enumerate(biggest_problem_areas, 1):
        avg_diff = sum(f['difference'] for f in failures_list) / len(failures_list)
        print(f"{i}. {period}: {len(failures_list)} cases, avg {avg_diff:.1f} days off")
    
    print(f"\n📋 SPECIFIC QUESTIONS TO ASK:")
    
    print(f"\n1. PROCESS & DECISION MAKING:")
    print(f"   • What's your step-by-step process for each date?")
    print(f"   • Do you ever override the 'normal' calculation? When and why?")
    print(f"   • Are there judgment calls or subjective decisions?")
    print(f"   • Do you consider anything beyond holidays and weekends?")
    
    print(f"\n2. SPECIAL PERIODS:")
    print(f"   • December/Christmas: What are the actual rules? (We get 0% accuracy)")
    print(f"   • Month-end dates: Any special handling for days 25-31?")
    print(f"   • Month-start dates: Any special handling for days 1-5?")
    
    print(f"\n3. EXTERNAL FACTORS:")
    print(f"   • Do you consider business operational needs?")
    print(f"   • Are there client-specific requirements?")
    print(f"   • Bank processing schedules or constraints?")
    print(f"   • Do you try to avoid certain payment dates?")
    
    print(f"\n4. CONSISTENCY RULES:")
    print(f"   • Do you try to keep consecutive days with same payment date?")
    print(f"   • How do you handle situations where the 'normal' rule gives weird results?")
    print(f"   • Any rules about minimum/maximum gaps between run date and payment date?")
    
    print(f"\n5. HISTORICAL CONTEXT:")
    print(f"   • Have the rules changed over the years?")
    print(f"   • Are there regional or jurisdictional differences?")
    print(f"   • Any informal practices that became standard?")
    
    # Show them specific problematic cases
    print(f"\n6. SPECIFIC CASES TO REVIEW WITH THEM:")
    worst_cases = sorted(failures, key=lambda x: x['difference'], reverse=True)[:5]
    for i, case in enumerate(worst_cases, 1):
        date_str = f"{case['year']}-{case['month']:02d}-{case['day']:02d}"
        print(f"   {i}. {date_str} ({case['weekday']}): We predict {case['predicted']}, truth is {case['ground_truth']} (diff: {case['difference']})")
    
    print(f"\n💡 ACTIONABLE OUTCOMES:")
    print(f"   • Get them to walk through their actual process for 5-10 problem dates")
    print(f"   • Ask for any written rules, guidelines, or documentation")
    print(f"   • Identify any 'soft' rules or preferences they follow")
    print(f"   • See if they can explain the Christmas period logic")
    print(f"   • Ask if they'd be willing to validate our algorithm improvements")


if __name__ == "__main__":
    analyze_failure_patterns()
