#!/usr/bin/env python3
"""
Show specific examples of where algorithm fails vs ground truth
"""

from rapid_test_framework import RapidTester
from payment_schedule_generator import Table109Generator
from datetime import datetime
import calendar


def optimized_algorithm(run_date):
    """Optimized algorithm wrapper"""
    generator = Table109Generator(run_date.year)
    return generator.calculate_payment_date(run_date)


def show_specific_examples():
    """Show specific date examples of failures"""
    tester = RapidTester()
    
    print("SPECIFIC EXAMPLES: GROUND TRUTH vs ALGORITHM")
    print("=" * 70)
    
    # Collect failures
    failures = []
    
    for (year, month), month_data in tester.ground_truth.items():
        for day, gt_payment in month_data.items():
            run_date = datetime(year, month, day)
            
            try:
                predicted_payment = optimized_algorithm(run_date)
                diff = abs(predicted_payment - gt_payment)
                
                if diff > 0:  # Only failures
                    failures.append({
                        'date': run_date,
                        'date_str': f"{year}-{month:02d}-{day:02d}",
                        'weekday': run_date.strftime('%A'),
                        'month_name': calendar.month_name[month],
                        'predicted': predicted_payment,
                        'ground_truth': gt_payment,
                        'difference': diff
                    })
                    
            except Exception as e:
                continue
    
    # Show examples by category
    show_cross_month_examples(failures)
    show_christmas_examples(failures)
    show_january_examples(failures) 
    show_typical_off_by_one_examples(failures)


def show_cross_month_examples(failures):
    """Show the devastating 31->1 pattern"""
    print(f"\n🔴 CROSS-MONTH BOUNDARY DISASTERS (31 → 1 pattern)")
    print(f"{'Date':<12} {'Day':<10} {'Our Pred':<8} {'Ground Truth':<12} {'Context'}")
    print(f"{'-'*60}")
    
    cross_month_failures = [f for f in failures if f['difference'] >= 25]
    
    for failure in sorted(cross_month_failures, key=lambda x: x['difference'], reverse=True)[:10]:
        context = f"{failure['month_name']} {failure['date'].day}"
        if failure['date'].day <= 5:
            context += " (Month Start)"
        
        print(f"{failure['date_str']:<12} {failure['weekday']:<10} {failure['predicted']:>6} {failure['ground_truth']:>10} {context}")
    
    print(f"\n💡 Pattern: We predict end-of-previous-month (31), truth is beginning-of-current-month (1)")


def show_christmas_examples(failures):
    """Show Christmas period failures"""
    print(f"\n🎄 CHRISTMAS PERIOD FAILURES")
    print(f"{'Date':<12} {'Day':<10} {'Our Pred':<8} {'Ground Truth':<12} {'Difference'}")
    print(f"{'-'*60}")
    
    christmas_failures = [f for f in failures if f['date'].month == 12 and f['date'].day >= 20]
    
    for failure in sorted(christmas_failures, key=lambda x: (x['date'].year, x['date'].day))[:15]:
        print(f"{failure['date_str']:<12} {failure['weekday']:<10} {failure['predicted']:>6} {failure['ground_truth']:>10} {failure['difference']:>8}")
    
    print(f"\n💡 Pattern: Christmas period has complex clustering we don't understand")


def show_january_examples(failures):
    """Show January failures"""
    print(f"\n❄️  JANUARY PERIOD FAILURES")
    print(f"{'Date':<12} {'Day':<10} {'Our Pred':<8} {'Ground Truth':<12} {'Difference'}")
    print(f"{'-'*60}")
    
    january_failures = [f for f in failures if f['date'].month == 1 and f['date'].day <= 10]
    
    for failure in sorted(january_failures, key=lambda x: (x['date'].year, x['date'].day))[:10]:
        print(f"{failure['date_str']:<12} {failure['weekday']:<10} {failure['predicted']:>6} {failure['ground_truth']:>10} {failure['difference']:>8}")
    
    print(f"\n💡 Pattern: January logic still has edge cases we miss")


def show_typical_off_by_one_examples(failures):
    """Show typical 1-2 day differences"""
    print(f"\n📊 TYPICAL OFF-BY-1-OR-2 EXAMPLES (Most Common)")
    print(f"{'Date':<12} {'Day':<10} {'Our Pred':<8} {'Ground Truth':<12} {'Difference'}")
    print(f"{'-'*60}")
    
    small_failures = [f for f in failures if 1 <= f['difference'] <= 2]
    
    # Show a representative sample
    for failure in small_failures[:15]:
        print(f"{failure['date_str']:<12} {failure['weekday']:<10} {failure['predicted']:>6} {failure['ground_truth']:>10} {failure['difference']:>8}")
    
    print(f"\n💡 Pattern: These are close - often just timing/clustering differences")
    print(f"Total off-by-1-or-2 cases: {len(small_failures)} ({len(small_failures)/len(failures)*100:.1f}% of all failures)")


if __name__ == "__main__":
    show_specific_examples()
