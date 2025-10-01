#!/usr/bin/env python3
"""
Enhanced Quality Metrics for Payment Schedule Algorithm
Provides detailed breakdown of prediction offsets: 0, 1, 2, 3+ days
Target: Maximum 2 days offset acceptable
"""

import re
import calendar
from datetime import datetime, timedelta
import os
from collections import defaultdict
import holidays
from payment_schedule_generator import Table109Generator
from rapid_test_framework import RapidTester


class EnhancedQualityTester(RapidTester):
    """Enhanced tester with granular offset metrics"""
    
    def test_algorithm_with_detailed_metrics(self, algorithm_func, test_cases=None):
        """Test algorithm with detailed offset breakdown"""
        results = {
            'total': 0,
            'offset_0': 0,    # Perfect matches
            'offset_1': 0,    # 1 day off  
            'offset_2': 0,    # 2 days off
            'offset_3_plus': 0,  # 3+ days off
            'by_period': defaultdict(lambda: {
                'total': 0, 'offset_0': 0, 'offset_1': 0, 
                'offset_2': 0, 'offset_3_plus': 0
            }),
            'detailed_errors': [],
            'large_errors': []  # Errors > 10 days for special attention
        }
        
        test_data = test_cases or self.ground_truth
        
        for (year, month), month_data in test_data.items():
            for day, gt_payment in month_data.items():
                run_date = datetime(year, month, day)
                
                try:
                    predicted_payment = algorithm_func(run_date)
                    
                    results['total'] += 1
                    diff = abs(predicted_payment - gt_payment)
                    
                    # Track by period
                    period = self._get_period(year, month, day)
                    results['by_period'][period]['total'] += 1
                    
                    # Categorize by offset
                    if diff == 0:
                        results['offset_0'] += 1
                        results['by_period'][period]['offset_0'] += 1
                    elif diff == 1:
                        results['offset_1'] += 1
                        results['by_period'][period]['offset_1'] += 1
                    elif diff == 2:
                        results['offset_2'] += 1
                        results['by_period'][period]['offset_2'] += 1
                    else:  # 3+ days
                        results['offset_3_plus'] += 1
                        results['by_period'][period]['offset_3_plus'] += 1
                        
                        # Track detailed errors for 3+ day offsets
                        error_info = {
                            'date': f"{year}-{month:02d}-{day:02d}",
                            'predicted': predicted_payment,
                            'ground_truth': gt_payment,
                            'offset': diff,
                            'period': period
                        }
                        results['detailed_errors'].append(error_info)
                        
                        # Special attention to very large errors
                        if diff > 10:
                            results['large_errors'].append(error_info)
                
                except Exception as e:
                    results['detailed_errors'].append({
                        'date': f"{year}-{month:02d}-{day:02d}",
                        'error': str(e)
                    })
        
        return results
    
    def print_enhanced_results(self, results, algorithm_name="Algorithm"):
        """Print detailed results with offset breakdown"""
        total = results['total']
        if total == 0:
            print("No test cases found!")
            return
            
        print(f"\n{'='*60}")
        print(f"ENHANCED QUALITY METRICS: {algorithm_name}")
        print(f"{'='*60}")
        print(f"Total Test Cases: {total:,}")
        
        # Main quality breakdown
        print(f"\n🎯 PREDICTION QUALITY BREAKDOWN:")
        print(f"{'Offset Level':<15} {'Count':<8} {'Percentage':<12} {'Status'}")
        print(f"{'-'*15} {'-'*8} {'-'*12} {'-'*20}")
        
        offset_0_pct = results['offset_0'] / total * 100
        print(f"{'0 days (Perfect)':<15} {results['offset_0']:<8} {offset_0_pct:<11.1f}% ✅ Excellent")
        
        offset_1_pct = results['offset_1'] / total * 100
        print(f"{'1 day':<15} {results['offset_1']:<8} {offset_1_pct:<11.1f}% ✅ Good")
        
        offset_2_pct = results['offset_2'] / total * 100
        print(f"{'2 days':<15} {results['offset_2']:<8} {offset_2_pct:<11.1f}% ✅ Acceptable")
        
        offset_3_pct = results['offset_3_plus'] / total * 100
        print(f"{'3+ days':<15} {results['offset_3_plus']:<8} {offset_3_pct:<11.1f}% ❌ Beyond Target")
        
        # Target achievement
        within_target = results['offset_0'] + results['offset_1'] + results['offset_2']
        within_target_pct = within_target / total * 100
        
        print(f"\n🎯 TARGET ACHIEVEMENT (≤2 days offset):")
        print(f"   Within Target: {within_target:,}/{total:,} ({within_target_pct:.1f}%)")
        print(f"   Beyond Target: {results['offset_3_plus']:,}/{total:,} ({offset_3_pct:.1f}%)")
        
        if within_target_pct >= 95.0:
            print(f"   🏆 EXCELLENT: Exceeds 95% target achievement!")
        elif within_target_pct >= 90.0:
            print(f"   ✅ GOOD: Meets 90%+ target achievement")
        elif within_target_pct >= 85.0:
            print(f"   ⚠️  ACCEPTABLE: Meets 85%+ target achievement")
        else:
            print(f"   ❌ NEEDS IMPROVEMENT: Below 85% target achievement")
        
        # Period breakdown
        print(f"\n📊 PERFORMANCE BY PERIOD:")
        print(f"{'Period':<18} {'Total':<6} {'Perfect':<8} {'1-day':<6} {'2-day':<6} {'3+ day':<7} {'Within Target'}")
        print(f"{'-'*18} {'-'*6} {'-'*8} {'-'*6} {'-'*6} {'-'*7} {'-'*12}")
        
        for period in sorted(results['by_period'].keys()):
            data = results['by_period'][period]
            if data['total'] > 0:
                within_period = data['offset_0'] + data['offset_1'] + data['offset_2']
                within_pct = within_period / data['total'] * 100
                
                print(f"{period:<18} {data['total']:<6} "
                      f"{data['offset_0']:<8} {data['offset_1']:<6} {data['offset_2']:<6} "
                      f"{data['offset_3_plus']:<7} {within_pct:>11.1f}%")
        
        # Problem cases analysis
        if results['detailed_errors']:
            beyond_target = [e for e in results['detailed_errors'] if 'offset' in e and e['offset'] > 2]
            
            print(f"\n❌ BEYOND TARGET CASES ({len(beyond_target)} cases):")
            if len(beyond_target) <= 10:
                print(f"{'Date':<12} {'Predicted':<10} {'Actual':<8} {'Offset':<7} {'Period'}")
                print(f"{'-'*12} {'-'*10} {'-'*8} {'-'*7} {'-'*15}")
                for error in beyond_target:
                    print(f"{error['date']:<12} {error['predicted']:<10} "
                          f"{error['ground_truth']:<8} {error['offset']:<7} {error['period']}")
            else:
                print(f"   Too many to show individually. Worst offenders:")
                worst = sorted(beyond_target, key=lambda x: x['offset'], reverse=True)[:5]
                for error in worst:
                    print(f"   {error['date']}: off by {error['offset']} days "
                          f"(pred: {error['predicted']}, actual: {error['ground_truth']})")
        
        # Large errors special attention
        if results['large_errors']:
            print(f"\n🚨 LARGE ERRORS (>10 days): {len(results['large_errors'])} cases")
            for error in results['large_errors'][:3]:  # Show top 3
                print(f"   {error['date']}: off by {error['offset']} days "
                      f"(pred: {error['predicted']}, actual: {error['ground_truth']})")


def test_current_algorithm_wrapper(run_date):
    """Wrapper function for testing current optimized algorithm"""
    try:
        generator = Table109Generator(run_date.year)
        return generator.calculate_payment_date(run_date)
    except Exception as e:
        print(f"Error testing algorithm for {run_date}: {e}")
        return 1


def main():
    tester = EnhancedQualityTester()
    
    print("ENHANCED QUALITY METRICS TESTING")
    print("Target: Maximum 2 days offset for payment predictions")
    print("Testing against all available historical data (2014-2018, 2020-2026)")
    
    # Test current optimized algorithm with enhanced metrics
    results = tester.test_algorithm_with_detailed_metrics(test_current_algorithm_wrapper)
    tester.print_enhanced_results(results, "Current Optimized Algorithm")
    
    print(f"\n🔍 DATA COVERAGE:")
    years_tested = set()
    for (year, month) in tester.ground_truth.keys():
        years_tested.add(year)
    print(f"   Years: {sorted(years_tested)}")
    print(f"   Total dates tested: {results['total']:,}")


if __name__ == "__main__":
    main()
