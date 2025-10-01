#!/usr/bin/env python3
"""
Algorithm Performance Tester - TABLE AGNOSTIC VERSION
Tests payment schedule algorithm against both Table 107 and Table 109 historical data.
Provides comprehensive performance metrics for each table type.
"""

import os
import re
import calendar
import argparse
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


def log_beyond_target_errors(errors, table_type, output_dir=None):
    """Log all 3+ day errors to a timestamped file."""
    if output_dir:
        filename = os.path.join(output_dir, f"beyond_target_errors_table_{table_type}.txt")
        print_log = False  # Don't print when saving to report folder
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"beyond_target_errors_table_{table_type}_{timestamp}.txt"
        print_log = True
    
    try:
        with open(filename, 'w') as f:
            f.write(f"BEYOND TARGET ERRORS (3+ days) - TABLE {table_type}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            # Sort errors by error magnitude (worst first)
            sorted_errors = sorted(errors, key=lambda x: x['error'], reverse=True)
            
            f.write(f"Total errors: {len(sorted_errors)}\n\n")
            
            # Group by error magnitude
            error_groups = {}
            for error in sorted_errors:
                error_days = error['error']
                if error_days not in error_groups:
                    error_groups[error_days] = []
                error_groups[error_days].append(error)
            
            # Write summary by error magnitude
            f.write("SUMMARY BY ERROR MAGNITUDE:\n")
            f.write("-" * 30 + "\n")
            for error_days in sorted(error_groups.keys(), reverse=True):
                count = len(error_groups[error_days])
                f.write(f"{error_days:2d} days off: {count:3d} cases\n")
            f.write("\n")
            
            # Write detailed list
            f.write("DETAILED ERROR LIST:\n")
            f.write("-" * 30 + "\n")
            f.write("Date       | Predicted | Actual | Error\n")
            f.write("-" * 40 + "\n")
            
            for error in sorted_errors:
                f.write(f"{error['date']} |    {error['predicted']:2d}     |   {error['actual']:2d}   | {error['error']:2d} days\n")
        
        if print_log:
            print(f"📄 Logged {len(errors)} beyond-target errors to: {filename}")
        
        return filename
        
    except Exception as e:
        if print_log:
            print(f"❌ Error writing log file {filename}: {e}")
        return None


def test_table_performance(table_type, output_dir=None):
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
    all_beyond_target_errors = []  # Store all 3+ day errors for logging
    
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
                # Store all 3+ day errors for logging
                error_info = {
                    'date': f"{year}-{month:02d}-{day:02d}",
                    'predicted': predicted_payment,
                    'actual': actual_payment,
                    'error': error,
                    'table_type': table_type
                }
                all_beyond_target_errors.append(error_info)
                
                if error > 10:
                    large_errors.append(error_info)
    
    # Log all 3+ day errors to file only if save_report is enabled
    if all_beyond_target_errors and output_dir:
        log_beyond_target_errors(all_beyond_target_errors, table_type, output_dir)
    
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
        'all_beyond_target_errors': all_beyond_target_errors,
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
    print("\n" + "=" * 95)
    print("📊 COMPARATIVE PERFORMANCE SUMMARY")
    print("=" * 95)
    
    if not table_107_results and not table_109_results:
        print("❌ No results to compare")
        return
        
    print()
    print("┌─────────────────────────┬─────────────────────────────┬─────────────────────────────┐")
    print("│         METRIC          │          TABLE 107          │          TABLE 109          │")
    print("│                         │   Count   │        %        │   Count   │        %        │")
    print("├─────────────────────────┼───────────┼─────────────────┼───────────┼─────────────────┤")
    
    # Test cases
    cases_107 = table_107_results['total_cases'] if table_107_results else 0
    cases_109 = table_109_results['total_cases'] if table_109_results else 0
    print(f"│ Total Test Cases        │ {cases_107:>7,} │      100.0%     │ {cases_109:>7,} │      100.0%     │")
    print("├─────────────────────────┼───────────┼─────────────────┼───────────┼─────────────────┤")
    
    # Perfect matches
    perfect_107_count = table_107_results['perfect_matches'] if table_107_results else 0
    perfect_107_pct = table_107_results['perfect_pct'] if table_107_results else 0
    perfect_109_count = table_109_results['perfect_matches'] if table_109_results else 0
    perfect_109_pct = table_109_results['perfect_pct'] if table_109_results else 0
    print(f"│ Perfect Matches (0 days)│ {perfect_107_count:>7,} │      {perfect_107_pct:>5.1f}%     │ {perfect_109_count:>7,} │      {perfect_109_pct:>5.1f}%     │")
    
    # 1-day offset
    one_day_107_count = table_107_results['one_day_errors'] if table_107_results else 0
    one_day_107_pct = table_107_results['one_day_pct'] if table_107_results else 0
    one_day_109_count = table_109_results['one_day_errors'] if table_109_results else 0
    one_day_109_pct = table_109_results['one_day_pct'] if table_109_results else 0
    print(f"│ 1-Day Offset            │ {one_day_107_count:>7,} │      {one_day_107_pct:>5.1f}%     │ {one_day_109_count:>7,} │      {one_day_109_pct:>5.1f}%     │")
    
    # 2-day offset
    two_day_107_count = table_107_results['two_day_errors'] if table_107_results else 0
    two_day_107_pct = table_107_results['two_day_pct'] if table_107_results else 0
    two_day_109_count = table_109_results['two_day_errors'] if table_109_results else 0
    two_day_109_pct = table_109_results['two_day_pct'] if table_109_results else 0
    print(f"│ 2-Day Offset            │ {two_day_107_count:>7,} │      {two_day_107_pct:>5.1f}%     │ {two_day_109_count:>7,} │      {two_day_109_pct:>5.1f}%     │")
    
    # 3+ day offset (beyond target)
    beyond_107_count = table_107_results['beyond_target_errors'] if table_107_results else 0
    beyond_107_pct = table_107_results['beyond_target_pct'] if table_107_results else 0
    beyond_109_count = table_109_results['beyond_target_errors'] if table_109_results else 0
    beyond_109_pct = table_109_results['beyond_target_pct'] if table_109_results else 0
    print(f"│ 3+ Day Offset           │ {beyond_107_count:>7,} │      {beyond_107_pct:>5.1f}%     │ {beyond_109_count:>7,} │      {beyond_109_pct:>5.1f}%     │")
    
    print("├─────────────────────────┼───────────┼─────────────────┼───────────┼─────────────────┤")
    
    # Within target (≤2 days)
    within_107_count = table_107_results['within_target'] if table_107_results else 0
    within_107_pct = table_107_results['within_target_pct'] if table_107_results else 0
    within_109_count = table_109_results['within_target'] if table_109_results else 0
    within_109_pct = table_109_results['within_target_pct'] if table_109_results else 0
    print(f"│ Within Target (≤2 days) │ {within_107_count:>7,} │      {within_107_pct:>5.1f}%     │ {within_109_count:>7,} │      {within_109_pct:>5.1f}%     │")
    
    print("├─────────────────────────┼───────────┼─────────────────┼───────────┼─────────────────┤")
    
    # Large errors
    large_107 = len(table_107_results['large_errors']) if table_107_results else 0
    large_109 = len(table_109_results['large_errors']) if table_109_results else 0
    print(f"│ Large Errors (>10 days) │ {large_107:>7,} │        —        │ {large_109:>7,} │        —        │")
    
    print("└─────────────────────────┴───────────┴─────────────────┴───────────┴─────────────────┘")
    


def capture_console_output(func, *args, **kwargs):
    """Capture console output for saving to file."""
    import io
    import sys
    
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()
    
    try:
        result = func(*args, **kwargs)
        output = captured_output.getvalue()
        return result, output
    finally:
        sys.stdout = old_stdout


def create_report_folder():
    """Create timestamped report folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"algorithm_test_report_{timestamp}"
    
    try:
        os.makedirs(folder_name, exist_ok=True)
        return folder_name
    except Exception as e:
        print(f"❌ Error creating report folder {folder_name}: {e}")
        return None


def comprehensive_algorithm_test(save_report=False):
    """Run comprehensive tests on both table types."""
    print("=" * 80)
    print("COMPREHENSIVE PAYMENT SCHEDULE ALGORITHM TEST")
    print("=" * 80)
    print("Testing algorithm performance on both Table 107 and Table 109")
    print("Using all available historical data with granular quality metrics")
    
    # Create report folder if needed
    report_folder = None
    if save_report:
        report_folder = create_report_folder()
        if report_folder:
            print(f"📁 Report will be saved to: {report_folder}")
    
    # Test Table 109 (our primary optimized table)
    table_109_results = test_table_performance("109", report_folder)
    if table_109_results:
        print_table_results(table_109_results)
    
    # Test Table 107 (Table 109 + 7 days)
    table_107_results = test_table_performance("107", report_folder)
    if table_107_results:
        print_table_results(table_107_results)
    
    # Print comparative summary
    print_comparative_summary(table_107_results, table_109_results)
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE TEST COMPLETE")
    print("=" * 80)
    
    # Save console output to file if requested
    if save_report and report_folder:
        try:
            # Capture the full test output by re-running with capture
            _, console_output = capture_console_output(
                run_test_without_save, table_107_results, table_109_results
            )
            
            # Save console output
            console_file = os.path.join(report_folder, "console_output.txt")
            with open(console_file, 'w') as f:
                f.write("COMPREHENSIVE PAYMENT SCHEDULE ALGORITHM TEST REPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                f.write(console_output)
            
            print(f"📄 Console output saved to: {console_file}")
            print(f"📁 Complete report saved in folder: {report_folder}")
            
        except Exception as e:
            print(f"❌ Error saving console output: {e}")


def run_test_without_save(table_107_results, table_109_results):
    """Run the display part of tests without saving (for output capture)."""
    if table_109_results:
        print_table_results(table_109_results)
    
    if table_107_results:
        print_table_results(table_107_results)
    
    print_comparative_summary(table_107_results, table_109_results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test payment schedule algorithm performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_algorithm.py                    # Run tests (no files saved)
  python test_algorithm.py --save-report     # Run tests and save report folder
        """
    )
    
    parser.add_argument(
        '--save-report',
        action='store_true',
        default=False,
        help='Save comprehensive report to timestamped folder (default: False)'
    )
    
    args = parser.parse_args()
    comprehensive_algorithm_test(save_report=args.save_report)