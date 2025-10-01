#!/usr/bin/env python3
"""
Improved Algorithm Tester - Testing Manager's New Rule
Compares current algorithm vs manager's new rule: Cycle+7 days, then -3 business days
"""

import re
import calendar
from datetime import datetime, timedelta
import os
from collections import defaultdict
import holidays
from payment_schedule_generator import Table109Generator
from rapid_test_framework import RapidTester


class ManagerRuleAlgorithm:
    """Implementation of manager's rule: Cycle+7 days, then -3 business days"""
    
    def __init__(self, year):
        self.year = year
        self.canadian_holidays = holidays.Canada(years=year)
        
    def is_weekend(self, date):
        return date.weekday() >= 5
    
    def is_holiday(self, date):
        return date in self.canadian_holidays
    
    def is_non_working_day(self, date):
        return self.is_weekend(date) or self.is_holiday(date)
    
    def calculate_payment_date(self, run_date):
        """Manager's rule: Cycle+7 days, then -3 business days"""
        
        # Step 1: Add 7 calendar days
        direct_deposit_date = run_date + timedelta(days=7)
        
        # Step 2: If it's a holiday, move to previous business day
        while self.is_non_working_day(direct_deposit_date):
            direct_deposit_date -= timedelta(days=1)
        
        # Step 3: Go back 3 business days
        business_days_back = 0
        payment_date = direct_deposit_date
        
        while business_days_back < 3:
            payment_date -= timedelta(days=1)
            if not self.is_non_working_day(payment_date):
                business_days_back += 1
        
        return payment_date.day


def test_manager_rule_wrapper(run_date):
    """Wrapper function for testing manager's rule"""
    try:
        algorithm = ManagerRuleAlgorithm(run_date.year)
        return algorithm.calculate_payment_date(run_date)
    except Exception as e:
        print(f"Error testing manager rule for {run_date}: {e}")
        return 1  # Default fallback


def test_current_algorithm_wrapper(run_date):
    """Wrapper function for testing current optimized algorithm"""
    try:
        generator = Table109Generator(run_date.year)
        return generator.calculate_payment_date(run_date)
    except Exception as e:
        print(f"Error testing current algorithm for {run_date}: {e}")
        return 1  # Default fallback


def main():
    tester = RapidTester()
    
    print("IMPROVED ALGORITHM TESTING - MANAGER'S RULE vs CURRENT ALGORITHM")
    print("=" * 80)
    
    # Test current optimized algorithm
    print("\n🔍 Testing CURRENT OPTIMIZED ALGORITHM...")
    current_results = tester.test_algorithm(test_current_algorithm_wrapper)
    tester.print_results(current_results, "Current Optimized Algorithm")
    
    # Test manager's new rule
    print("\n🔍 Testing MANAGER'S NEW RULE (Cycle+7, -3 business days)...")
    manager_results = tester.test_algorithm(test_manager_rule_wrapper)
    tester.print_results(manager_results, "Manager's New Rule")
    
    # Detailed comparison
    print(f"\n" + "=" * 80)
    print(f"DETAILED COMPARISON")
    print(f"=" * 80)
    
    current_total = current_results['total']
    manager_total = manager_results['total']
    
    if current_total > 0 and manager_total > 0:
        print(f"{'Metric':<25} {'Current Algo':<15} {'Manager Rule':<15} {'Difference'}")
        print(f"{'-'*25} {'-'*15} {'-'*15} {'-'*10}")
        
        current_perfect = current_results['perfect'] / current_total * 100
        manager_perfect = manager_results['perfect'] / manager_total * 100
        print(f"{'Perfect Accuracy':<25} {current_perfect:>13.1f}%  {manager_perfect:>13.1f}%  {manager_perfect-current_perfect:>+8.1f}%")
        
        current_practical = (current_results['perfect'] + current_results['close_1']) / current_total * 100
        manager_practical = (manager_results['perfect'] + manager_results['close_1']) / manager_total * 100
        print(f"{'Practical (≤1 day)':<25} {current_practical:>13.1f}%  {manager_practical:>13.1f}%  {manager_practical-current_practical:>+8.1f}%")
        
        current_acceptable = (current_results['perfect'] + current_results['close_1'] + current_results['close_2']) / current_total * 100
        manager_acceptable = (manager_results['perfect'] + manager_results['close_1'] + manager_results['close_2']) / manager_total * 100
        print(f"{'Acceptable (≤2 days)':<25} {current_acceptable:>13.1f}%  {manager_acceptable:>13.1f}%  {manager_acceptable-current_acceptable:>+8.1f}%")
        
        current_major = current_results['major_errors'] / current_total * 100
        manager_major = manager_results['major_errors'] / manager_total * 100
        print(f"{'Major Errors (>5 days)':<25} {current_major:>13.1f}%  {manager_major:>13.1f}%  {manager_major-current_major:>+8.1f}%")
        
        print(f"{'Total Test Cases':<25} {current_total:>13d}    {manager_total:>13d}")
        
        # Period comparison
        print(f"\n📊 PERFORMANCE BY PERIOD:")
        print(f"{'Period':<20} {'Current Algo':<15} {'Manager Rule':<15} {'Difference'}")
        print(f"{'-'*20} {'-'*15} {'-'*15} {'-'*10}")
        
        all_periods = set(current_results['by_period'].keys()) | set(manager_results['by_period'].keys())
        for period in sorted(all_periods):
            current_data = current_results['by_period'].get(period, {'total': 0, 'perfect': 0})
            manager_data = manager_results['by_period'].get(period, {'total': 0, 'perfect': 0})
            
            current_pct = current_data['perfect'] / current_data['total'] * 100 if current_data['total'] > 0 else 0
            manager_pct = manager_data['perfect'] / manager_data['total'] * 100 if manager_data['total'] > 0 else 0
            
            if current_data['total'] > 0 or manager_data['total'] > 0:
                print(f"{period:<20} {current_pct:>13.1f}%  {manager_pct:>13.1f}%  {manager_pct-current_pct:>+8.1f}%")
        
        # Recommendation
        print(f"\n🎯 RECOMMENDATION:")
        if manager_perfect > current_perfect:
            print(f"   ✅ Manager's rule shows {manager_perfect-current_perfect:+.1f}% improvement in perfect accuracy!")
            print(f"   📈 Consider adopting manager's rule as the new standard.")
        elif current_perfect > manager_perfect:
            print(f"   ✅ Current algorithm outperforms by {current_perfect-manager_perfect:+.1f}% in perfect accuracy.")
            print(f"   📈 Current optimized algorithm remains the best choice.")
        else:
            print(f"   ⚖️  Both algorithms show similar performance.")
            print(f"   📈 Consider hybrid approach or other factors for decision.")


if __name__ == "__main__":
    main()
