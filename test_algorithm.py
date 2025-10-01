#!/usr/bin/env python3
"""
Algorithm Performance Tester - TABLE AGNOSTIC VERSION
Tests payment schedule algorithm against both Table 107 and Table 109 historical data.
Provides comprehensive performance metrics for each table type.
"""

import os
import re
import calendar
from datetime import datetime
from collections import defaultdict
from payment_schedule_generator import PaymentScheduleGenerator


def load_all_historical_data(table_type):
    """Load all historical ground truth data for specified table type."""
    data = {}
    table_dir = "table_examples"
    
    if not os.path.exists(table_dir):
        print(f"❌ Error: {table_dir} directory not found")
        return {}
    
    print(f"\n📊 LOADING TABLE {table_type} HISTORICAL DATA")
    print("=" * 50)
    
    # Define available years for each table type
    if table_type == "109":
        available_years = [2014, 2015, 2016, 2017, 2018, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    elif table_type == "107":
        available_years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    else:
        print(f"❌ Error: Unsupported table type {table_type}")
        return {}
    
    # Load all available years for the table type
    loaded_years = []
    for year in available_years:
        file_path = f"{table_dir}/table_{table_type}_{year}.txt"
        if os.path.exists(file_path):
            print(f"Loading {file_path}...")
            year_data = parse_payment_table(file_path, year)
            data.update(year_data)
            loaded_years.append(year)
            # More accurate count of actual data entries
            actual_entries = sum(len(month_data) for month_data in year_data.values())
            print(f"  → Loaded {actual_entries:,} date entries for {year}")
    
    print(f"\n✅ Table {table_type} Summary:")
    print(f"  Years loaded: {loaded_years}")
    print(f"  Total months: {len(data)} month-entries") 
    total_entries = sum(len(month_data) for month_data in data.values())
    print(f"  Total test cases: {total_entries:,}")
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
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    return months.get(month_name)


def parse_month_data(month_section):
    """Parse individual month section."""
    data = {}
    lines = month_section.strip().split('\n')
    
    for line in lines:
        # Look for pattern: day : payment payment
        matches = re.findall(r'(\d{1,2})\s*:\s*(\d{1,2})\s+(\d{1,2})', line)
        for run_day, _, payment_day in matches:
            run_day = int(run_day)
            payment_day = int(payment_day)
            if 1 <= run_day <= 31 and 1 <= payment_day <= 31:
                data[run_day] = payment_day
    
    return data


def test_table_performance(table_type):
    """Test algorithm performance for a specific table type."""
    print(f"\n🧪 TESTING TABLE {table_type} PERFORMANCE")
    print("=" * 60)
    
    # Load ground truth data for this table type
    ground_truth = load_all_historical_data(table_type)
    if not ground_truth:
        print(f"❌ No Table {table_type} ground truth data loaded. Skipping tests.")
        return None
    
    # Initialize counters
    total_cases = 0
    perfect_matches = 0
    one_day_errors = 0
    two_day_errors = 0
    beyond_target_errors = 0
    large_errors = []
    
    # Test each case
    for (year, month), month_data in ground_truth.items():
        generator = PaymentScheduleGenerator(year, table_type)
        
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
                if error > 10:
                    large_errors.append({
                        'date': f"{year}-{month:02d}-{day:02d}",
                        'predicted': predicted_payment,
                        'actual': actual_payment,
                        'error': error
                    })
    
    # Calculate percentages
    if total_cases == 0:
        return None
        
    perfect_pct = (perfect_matches / total_cases) * 100
    one_day_pct = (one_day_errors / total_cases) * 100
    two_day_pct = (two_day_errors / total_cases) * 100
    beyond_target_pct = (beyond_target_errors / total_cases) * 100
    within_target = perfect_matches + one_day_errors + two_day_errors
    within_target_pct = (within_target / total_cases) * 100
    
    # Return results
    return {
        'table_type': table_type,
        'total_cases': total_cases,
        'perfect_matches': perfect_matches,
        'one_day_errors': one_day_errors,
        'two_day_errors': two_day_errors,
        'beyond_target_errors': beyond_target_errors,
        'large_errors': large_errors,
        'perfect_pct': perfect_pct,
        'one_day_pct': one_day_pct,
        'two_day_pct': two_day_pct,
        'beyond_target_pct': beyond_target_pct,
        'within_target': within_target,
        'within_target_pct': within_target_pct
    }


def print_table_results(results):
    """Print comprehensive results for a table type."""
    if not results:
        return
        
    table_type = results['table_type']
    total_cases = results['total_cases']
    
    print(f"\n📊 TABLE {table_type} PERFORMANCE RESULTS")
    print("=" * 50)
    print(f"Total Test Cases: {total_cases:,}")
    print()
    print("📈 PREDICTION QUALITY BREAKDOWN:")
    print(f"  Perfect (0 days):      {results['perfect_matches']:,} ({results['perfect_pct']:>5.1f}%) ✅")
    print(f"  1-day offset:          {results['one_day_errors']:,} ({results['one_day_pct']:>5.1f}%) ✅")
    print(f"  2-day offset:          {results['two_day_errors']:,} ({results['two_day_pct']:>5.1f}%) ✅") 
    print(f"  Beyond target (3+ days): {results['beyond_target_errors']:,} ({results['beyond_target_pct']:>5.1f}%) ❌")
    print()
    print("🎯 TARGET ACHIEVEMENT (≤2 days offset):")
    print(f"  Within Target: {results['within_target']:,}/{total_cases:,} ({results['within_target_pct']:>5.1f}%)")
    print(f"  Beyond Target: {results['beyond_target_errors']:,}/{total_cases:,} ({results['beyond_target_pct']:>5.1f}%)")
    
    if results['within_target_pct'] >= 95.0:
        print("  🏆 EXCELLENT: Exceeds 95% target achievement!")
    elif results['within_target_pct'] >= 85.0:
        print("  ✅ GOOD: Meets 85%+ target achievement")
    else:
        print("  ⚠️  NEEDS IMPROVEMENT: Below 90% target achievement")
    
    if results['large_errors']:
        print()
        print(f"🚨 LARGE ERRORS (>10 days): {len(results['large_errors'])} cases")
        print("  Worst offenders:")
        for error in results['large_errors'][:5]:
            print(f"    {error['date']}: predicted {error['predicted']}, actual {error['actual']} (off by {error['error']} days)")
        if len(results['large_errors']) > 5:
            print(f"    ... and {len(results['large_errors']) - 5} more")
    else:
        print()
        print("🚨 LARGE ERRORS (>10 days): 0 cases - Excellent!")


def print_comparative_summary(table_107_results, table_109_results):
    """Print comparative summary between table types."""
    print("\n" + "=" * 80)
    print("📊 COMPARATIVE PERFORMANCE SUMMARY")
    print("=" * 80)
    
    if not table_107_results and not table_109_results:
        print("❌ No results to compare")
        return
        
    print()
    print("┌─────────────────────────┬───────────────┬───────────────┐")
    print("│         METRIC          │   TABLE 107   │   TABLE 109   │")
    print("├─────────────────────────┼───────────────┼───────────────┤")
    
    # Test cases
    cases_107 = table_107_results['total_cases'] if table_107_results else 0
    cases_109 = table_109_results['total_cases'] if table_109_results else 0
    print(f"│ Total Test Cases        │ {cases_107:>11,} │ {cases_109:>11,} │")
    
    # Perfect matches
    perfect_107 = f"{table_107_results['perfect_pct']:>6.1f}%" if table_107_results else "    N/A"
    perfect_109 = f"{table_109_results['perfect_pct']:>6.1f}%" if table_109_results else "    N/A"
    print(f"│ Perfect Matches         │ {perfect_107:>11} │ {perfect_109:>11} │")
    
    # Within target
    within_107 = f"{table_107_results['within_target_pct']:>6.1f}%" if table_107_results else "    N/A"
    within_109 = f"{table_109_results['within_target_pct']:>6.1f}%" if table_109_results else "    N/A"
    print(f"│ Within Target (≤2 days) │ {within_107:>11} │ {within_109:>11} │")
    
    # Beyond target
    beyond_107 = f"{table_107_results['beyond_target_pct']:>6.1f}%" if table_107_results else "    N/A"
    beyond_109 = f"{table_109_results['beyond_target_pct']:>6.1f}%" if table_109_results else "    N/A"
    print(f"│ Beyond Target (3+ days) │ {beyond_107:>11} │ {beyond_109:>11} │")
    
    # Large errors
    large_107 = len(table_107_results['large_errors']) if table_107_results else 0
    large_109 = len(table_109_results['large_errors']) if table_109_results else 0
    print(f"│ Large Errors (>10 days) │ {large_107:>11} │ {large_109:>11} │")
    
    print("└─────────────────────────┴───────────────┴───────────────┘")
    


def comprehensive_algorithm_test():
    """Run comprehensive tests on both table types."""
    print("=" * 80)
    print("COMPREHENSIVE PAYMENT SCHEDULE ALGORITHM TEST")
    print("=" * 80)
    print("Testing algorithm performance on both Table 107 and Table 109")
    print("Using all available historical data with granular quality metrics")
    
    # Test Table 109 (our primary optimized table)
    table_109_results = test_table_performance("109")
    if table_109_results:
        print_table_results(table_109_results)
    
    # Test Table 107 (Table 109 + 7 days)
    table_107_results = test_table_performance("107")
    if table_107_results:
        print_table_results(table_107_results)
    
    # Print comparative summary
    print_comparative_summary(table_107_results, table_109_results)
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    comprehensive_algorithm_test()