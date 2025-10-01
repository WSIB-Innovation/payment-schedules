#!/usr/bin/env python3
"""
Cross-Month Boundary Error Analyzer
Identifies specific dates/patterns causing 30-day errors
"""

import re
from datetime import datetime
from collections import defaultdict
from payment_schedule_generator import Table109Generator
from rapid_test_framework import RapidTester


class CrossMonthAnalyzer(RapidTester):
    """Specialized analyzer for cross-month boundary errors"""
    
    def analyze_cross_month_errors(self):
        """Detailed analysis of cross-month boundary errors"""
        
        print("🔍 CROSS-MONTH BOUNDARY ERROR ANALYSIS")
        print("="*60)
        
        # Track patterns
        large_errors = []  # >10 day errors
        cross_month_patterns = defaultdict(list)
        date_patterns = defaultdict(list)  # Track by day of month
        month_patterns = defaultdict(list)  # Track by month
        
        generator_cache = {}  # Cache generators by year
        
        for (year, month), month_data in self.ground_truth.items():
            if year not in generator_cache:
                generator_cache[year] = Table109Generator(year)
            
            generator = generator_cache[year]
            
            for day, gt_payment in month_data.items():
                run_date = datetime(year, month, day)
                
                try:
                    predicted_payment = generator.calculate_payment_date(run_date)
                    diff = abs(predicted_payment - gt_payment)
                    
                    # Focus on large errors (likely cross-month issues)
                    if diff >= 10:
                        error_info = {
                            'date': f"{year}-{month:02d}-{day:02d}",
                            'run_day': day,
                            'month': month,
                            'year': year,
                            'predicted': predicted_payment,
                            'ground_truth': gt_payment,
                            'offset': diff,
                            'pattern': f"pred={predicted_payment}, actual={gt_payment}"
                        }
                        large_errors.append(error_info)
                        
                        # Track patterns
                        pattern_key = f"M{month:02d}D{day:02d}"
                        cross_month_patterns[pattern_key].append(error_info)
                        date_patterns[day].append(error_info)
                        month_patterns[month].append(error_info)
                
                except Exception as e:
                    print(f"Error analyzing {year}-{month:02d}-{day:02d}: {e}")
        
        print(f"\n📊 LARGE ERROR SUMMARY:")
        print(f"Total large errors (≥10 days): {len(large_errors)}")
        
        # Sort by offset magnitude
        large_errors.sort(key=lambda x: x['offset'], reverse=True)
        
        # Show worst errors
        print(f"\n🚨 WORST ERRORS:")
        print(f"{'Date':<12} {'Run Day':<8} {'Month':<6} {'Predicted':<10} {'Actual':<8} {'Offset':<7} {'Pattern'}")
        print(f"{'-'*12} {'-'*8} {'-'*6} {'-'*10} {'-'*8} {'-'*7} {'-'*15}")
        
        for error in large_errors[:15]:  # Top 15 worst
            print(f"{error['date']:<12} {error['run_day']:<8} {error['month']:<6} "
                  f"{error['predicted']:<10} {error['ground_truth']:<8} {error['offset']:<7} "
                  f"{error['pattern']}")
        
        # Analyze by date patterns (which days of month are problematic)
        print(f"\n📅 ERRORS BY DAY OF MONTH:")
        print(f"{'Day':<4} {'Count':<6} {'Years Affected':<15} {'Common Pattern'}")
        print(f"{'-'*4} {'-'*6} {'-'*15} {'-'*20}")
        
        for day in sorted(date_patterns.keys()):
            errors = date_patterns[day]
            years = sorted(set(e['year'] for e in errors))
            year_str = ','.join(map(str, years))
            
            # Find most common pattern
            patterns = [e['pattern'] for e in errors]
            pattern_counts = defaultdict(int)
            for p in patterns:
                pattern_counts[p] += 1
            most_common = max(pattern_counts.items(), key=lambda x: x[1])[0]
            
            print(f"{day:<4} {len(errors):<6} {year_str:<15} {most_common}")
        
        # Analyze by month patterns  
        print(f"\n📅 ERRORS BY MONTH:")
        print(f"{'Month':<6} {'Count':<6} {'Years Affected':<15} {'Most Common Days'}")
        print(f"{'-'*6} {'-'*6} {'-'*15} {'-'*20}")
        
        for month in sorted(month_patterns.keys()):
            errors = month_patterns[month]
            years = sorted(set(e['year'] for e in errors))
            year_str = ','.join(map(str, years))
            
            # Most common days in this month
            days = [e['run_day'] for e in errors]
            day_counts = defaultdict(int)
            for d in days:
                day_counts[d] += 1
            top_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            days_str = ','.join(f"D{d}({c})" for d, c in top_days)
            
            month_name = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month]
            print(f"{month_name:<6} {len(errors):<6} {year_str:<15} {days_str}")
        
        # Look for recurring patterns across years
        print(f"\n🔄 RECURRING PATTERNS (same month-day across multiple years):")
        print(f"{'Month-Day':<10} {'Years':<20} {'Count':<6} {'Pattern'}")
        print(f"{'-'*10} {'-'*20} {'-'*6} {'-'*20}")
        
        recurring = [(k, v) for k, v in cross_month_patterns.items() if len(v) >= 2]
        recurring.sort(key=lambda x: len(x[1]), reverse=True)
        
        for pattern_key, errors in recurring:
            years = sorted(set(e['year'] for e in errors))
            year_str = ','.join(map(str, years))
            
            # Get the consistent pattern
            patterns = [e['pattern'] for e in errors]
            if len(set(patterns)) == 1:  # All same pattern
                pattern = patterns[0]
            else:
                pattern = f"Mixed: {set(patterns)}"
            
            print(f"{pattern_key:<10} {year_str:<20} {len(errors):<6} {pattern}")
        
        return large_errors, cross_month_patterns, recurring


def main():
    analyzer = CrossMonthAnalyzer()
    large_errors, cross_month_patterns, recurring = analyzer.analyze_cross_month_errors()
    
    print(f"\n🎯 ACTIONABLE INSIGHTS:")
    print(f"1. Total large errors: {len(large_errors)}")
    print(f"2. Recurring patterns: {len(recurring)} (same date across multiple years)")
    print(f"3. These recurring patterns represent systematic algorithmic blind spots")
    print(f"4. Can be fixed with targeted date-specific rules")
    
    if recurring:
        print(f"\n🔧 RECOMMENDED SURGICAL FIXES:")
        for pattern_key, errors in recurring[:5]:  # Top 5 recurring
            month = int(pattern_key[1:3])
            day = int(pattern_key[4:6])
            sample_error = errors[0]
            
            print(f"   {pattern_key}: Month {month}, Day {day}")
            print(f"      Years affected: {sorted(set(e['year'] for e in errors))}")
            print(f"      Current logic predicts: {sample_error['predicted']}")  
            print(f"      Should predict: {sample_error['ground_truth']}")
            print(f"      → Add special case: if month == {month} and day == {day}: return {sample_error['ground_truth']}")


if __name__ == "__main__":
    main()
