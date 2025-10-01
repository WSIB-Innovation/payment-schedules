#!/usr/bin/env python3
"""
Manager's Rule Implementation and Comparison
Rule: "Cycle date + 7 calendar days = Direct Deposit date (if it's a holiday it must be previous Business Day)"
      "Direct Deposit date -3 Business Day = Processing Day"
"""

import calendar
from datetime import datetime, timedelta
import holidays
from payment_schedule_generator import Table109Generator
from rapid_test_framework import RapidTester

class ManagerRuleGenerator:
    """Implementation of manager's proposed rule"""
    
    def __init__(self, year):
        self.year = year
        self.canadian_holidays = holidays.Canada(years=year)
        
    def is_weekend(self, date):
        return date.weekday() >= 5
    
    def is_holiday(self, date):
        return date in self.canadian_holidays
    
    def is_non_working_day(self, date):
        return self.is_weekend(date) or self.is_holiday(date)
    
    def find_previous_business_day(self, date):
        """Find the previous business day if date is holiday/weekend"""
        current = date
        while self.is_non_working_day(current):
            current -= timedelta(days=1)
        return current
    
    def subtract_business_days(self, date, business_days):
        """Subtract N business days from a date"""
        current = date
        days_subtracted = 0
        
        while days_subtracted < business_days:
            current -= timedelta(days=1)
            if not self.is_non_working_day(current):
                days_subtracted += 1
                
        return current
    
    def calculate_payment_date(self, run_date):
        """Manager's Rule Implementation"""
        # Step 1: Cycle date + 7 calendar days = Direct Deposit date
        direct_deposit_date = run_date + timedelta(days=7)
        
        # Step 2: If Direct Deposit date is holiday/weekend, move to previous business day
        direct_deposit_date = self.find_previous_business_day(direct_deposit_date)
        
        # Step 3: Direct Deposit date - 3 business days = Processing Day (payment date)
        payment_date = self.subtract_business_days(direct_deposit_date, 3)
        
        return payment_date.day

def compare_algorithms():
    """Compare Manager's Rule vs Current Algorithm"""
    
    print("=== MANAGER'S RULE vs CURRENT ALGORITHM COMPARISON ===\n")
    
    # Load ground truth
    tester = RapidTester()
    ground_truth = tester.ground_truth
    if not ground_truth:
        print("❌ Could not load ground truth data")
        return
    
    total_cases = 0
    manager_perfect = 0
    current_perfect = 0
    manager_within_2 = 0
    current_within_2 = 0
    manager_beyond_target = 0
    current_beyond_target = 0
    
    # Ground truth structure is {(year, month): {day: gt_payment}}
    for (year, month), month_data in ground_truth.items():
        manager_gen = ManagerRuleGenerator(year)
        current_gen = Table109Generator(year)
        
        for day, actual_payment in month_data.items():
            total_cases += 1
            run_date = datetime(year, month, day)
            
            # Manager's rule prediction
            manager_pred = manager_gen.calculate_payment_date(run_date)
            manager_error = abs(manager_pred - actual_payment)
            
            # Current algorithm prediction  
            current_pred = current_gen.calculate_payment_date(run_date)
            current_error = abs(current_pred - actual_payment)
            
            # Count perfect matches
            if manager_error == 0:
                manager_perfect += 1
            if current_error == 0:
                current_perfect += 1
                
            # Count within target (≤2 days)
            if manager_error <= 2:
                manager_within_2 += 1
            if current_error <= 2:
                current_within_2 += 1
                
            # Count beyond target
            if manager_error > 2:
                manager_beyond_target += 1
            if current_error > 2:
                current_beyond_target += 1
    
    print(f"📊 COMPARISON RESULTS (Total cases: {total_cases})")
    print("="*60)
    print(f"{'Metric':<25} {'Manager Rule':<15} {'Current Algo':<15}")
    print("="*60)
    print(f"{'Perfect (0 days)':<25} {manager_perfect:>6} ({manager_perfect/total_cases*100:>5.1f}%) {current_perfect:>6} ({current_perfect/total_cases*100:>5.1f}%)")
    print(f"{'Within Target (≤2 days)':<25} {manager_within_2:>6} ({manager_within_2/total_cases*100:>5.1f}%) {current_within_2:>6} ({current_within_2/total_cases*100:>5.1f}%)")
    print(f"{'Beyond Target (>2 days)':<25} {manager_beyond_target:>6} ({manager_beyond_target/total_cases*100:>5.1f}%) {current_beyond_target:>6} ({current_beyond_target/total_cases*100:>5.1f}%)")
    print("="*60)
    
    # Determine winner
    print("\n🏆 VERDICT:")
    if manager_perfect > current_perfect:
        print(f"   Manager's Rule WINS with {manager_perfect - current_perfect} more perfect matches")
    elif current_perfect > manager_perfect:
        print(f"   Current Algorithm WINS with {current_perfect - manager_perfect} more perfect matches")
    else:
        print("   TIE in perfect matches")
        
    if manager_within_2 > current_within_2:
        print(f"   Manager's Rule has {manager_within_2 - current_within_2} more cases within target")
    elif current_within_2 > manager_within_2:
        print(f"   Current Algorithm has {current_within_2 - manager_within_2} more cases within target")

if __name__ == "__main__":
    compare_algorithms()
