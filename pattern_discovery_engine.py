#!/usr/bin/env python3
"""
Pattern Discovery Engine - Hunt for Hidden Algorithmic Patterns
Analyzes remaining 5.8% problematic cases to discover new systematic patterns
"""

import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import calendar
import holidays
from payment_schedule_generator import Table109Generator
from rapid_test_framework import RapidTester


class PatternDiscoveryEngine(RapidTester):
    """Advanced pattern discovery for remaining algorithmic blind spots"""
    
    def __init__(self):
        super().__init__()
        self.generator_cache = {}
        
    def get_generator(self, year):
        if year not in self.generator_cache:
            self.generator_cache[year] = Table109Generator(year)
        return self.generator_cache[year]
    
    def analyze_remaining_problematic_cases(self):
        """Comprehensive analysis of all remaining beyond-target cases"""
        
        print("🔍 PATTERN DISCOVERY ENGINE - HUNTING FOR HIDDEN RULES")
        print("="*70)
        
        # Collect all beyond-target cases (>2 days offset)
        problematic_cases = []
        all_cases = []
        
        for (year, month), month_data in self.ground_truth.items():
            generator = self.get_generator(year)
            
            for day, gt_payment in month_data.items():
                run_date = datetime(year, month, day)
                
                try:
                    predicted_payment = generator.calculate_payment_date(run_date)
                    diff = abs(predicted_payment - gt_payment)
                    
                    case_info = {
                        'date': f"{year}-{month:02d}-{day:02d}",
                        'run_date': run_date,
                        'year': year,
                        'month': month,
                        'day': day,
                        'predicted': predicted_payment,
                        'ground_truth': gt_payment,
                        'offset': diff,
                        'weekday': run_date.strftime('%A'),
                        'weekday_num': run_date.weekday(),
                        'is_month_start': day <= 5,
                        'is_month_end': day >= calendar.monthrange(year, month)[1] - 4,
                        'quarter': (month - 1) // 3 + 1,
                        'is_quarter_end': month in [3, 6, 9, 12],
                        'is_year_end': month == 12,
                        'period': self._get_period(year, month, day)
                    }
                    
                    all_cases.append(case_info)
                    
                    if diff > 2:  # Beyond target cases
                        problematic_cases.append(case_info)
                
                except Exception as e:
                    print(f"Error analyzing {year}-{month:02d}-{day:02d}: {e}")
        
        print(f"\n📊 OVERVIEW:")
        print(f"Total cases: {len(all_cases):,}")
        print(f"Beyond target (>2 days): {len(problematic_cases)} ({len(problematic_cases)/len(all_cases)*100:.1f}%)")
        
        return problematic_cases, all_cases
    
    def discover_christmas_patterns(self, problematic_cases):
        """Deep dive into Christmas period underperformance"""
        
        print(f"\n🎄 CHRISTMAS PERIOD DEEP ANALYSIS:")
        print(f"Current performance: 63.5% vs 95.2% regular periods")
        
        christmas_problems = [case for case in problematic_cases if case['period'] == 'Christmas_Period']
        
        print(f"\nChristmas beyond-target cases: {len(christmas_problems)}")
        
        if christmas_problems:
            print(f"\n{'Date':<12} {'Day':<4} {'Predicted':<10} {'Actual':<8} {'Offset':<7} {'Weekday'}")
            print(f"{'-'*12} {'-'*4} {'-'*10} {'-'*8} {'-'*7} {'-'*10}")
            
            christmas_problems.sort(key=lambda x: (x['month'], x['day']))
            for case in christmas_problems:
                print(f"{case['date']:<12} {case['day']:<4} {case['predicted']:<10} "
                      f"{case['ground_truth']:<8} {case['offset']:<7} {case['weekday']}")
            
            # Analyze patterns
            day_patterns = Counter(case['day'] for case in christmas_problems)
            year_patterns = Counter(case['year'] for case in christmas_problems)
            
            print(f"\n🔍 Christmas Day Patterns:")
            for day, count in sorted(day_patterns.items()):
                print(f"   Dec {day}: {count} errors")
                
            print(f"\n🔍 Christmas Year Patterns:")
            for year, count in sorted(year_patterns.items()):
                print(f"   {year}: {count} errors")
        
        return christmas_problems
    
    def discover_consecutive_clustering_patterns(self, problematic_cases):
        """Look for consecutive day clustering patterns"""
        
        print(f"\n📅 CONSECUTIVE DAY CLUSTERING ANALYSIS:")
        
        # Group by year-month, then look for consecutive days
        month_groups = defaultdict(list)
        for case in problematic_cases:
            key = f"{case['year']}-{case['month']:02d}"
            month_groups[key].append(case)
        
        consecutive_clusters = []
        
        for month_key, cases in month_groups.items():
            if len(cases) >= 2:  # At least 2 errors in same month
                cases.sort(key=lambda x: x['day'])
                
                # Find consecutive sequences
                current_cluster = [cases[0]]
                
                for i in range(1, len(cases)):
                    if cases[i]['day'] == cases[i-1]['day'] + 1:  # Consecutive
                        current_cluster.append(cases[i])
                    else:
                        if len(current_cluster) >= 2:
                            consecutive_clusters.append(current_cluster.copy())
                        current_cluster = [cases[i]]
                
                # Don't forget the last cluster
                if len(current_cluster) >= 2:
                    consecutive_clusters.append(current_cluster)
        
        print(f"Found {len(consecutive_clusters)} consecutive error clusters:")
        
        for i, cluster in enumerate(consecutive_clusters):
            if len(cluster) >= 2:
                start_day = cluster[0]['day']
                end_day = cluster[-1]['day']
                month = cluster[0]['month']
                year = cluster[0]['year']
                
                month_name = calendar.month_name[month]
                print(f"\n   Cluster {i+1}: {month_name} {year}, days {start_day}-{end_day} ({len(cluster)} consecutive errors)")
                
                # Show pattern
                patterns = [f"pred={c['predicted']}, actual={c['ground_truth']}" for c in cluster]
                if len(set(patterns)) == 1:
                    print(f"      Consistent pattern: {patterns[0]}")
                else:
                    print(f"      Mixed patterns: {set(patterns)}")
        
        return consecutive_clusters
    
    def discover_seasonal_quarterly_patterns(self, problematic_cases):
        """Look for seasonal/quarterly business patterns"""
        
        print(f"\n📈 SEASONAL & QUARTERLY PATTERN ANALYSIS:")
        
        # Group by various time periods
        monthly_errors = Counter(case['month'] for case in problematic_cases)
        quarterly_errors = Counter(case['quarter'] for case in problematic_cases)
        weekday_errors = Counter(case['weekday'] for case in problematic_cases)
        
        print(f"\n🗓️  Errors by Month:")
        total_errors = len(problematic_cases)
        for month in range(1, 13):
            count = monthly_errors[month]
            pct = count / total_errors * 100 if total_errors > 0 else 0
            month_name = calendar.month_name[month][:3]
            if count > 0:
                print(f"   {month_name}: {count:2d} errors ({pct:4.1f}%)")
        
        print(f"\n📊 Errors by Quarter:")
        for quarter in range(1, 5):
            count = quarterly_errors[quarter]
            pct = count / total_errors * 100 if total_errors > 0 else 0
            if count > 0:
                print(f"   Q{quarter}: {count:2d} errors ({pct:4.1f}%)")
        
        print(f"\n📅 Errors by Weekday:")
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            count = weekday_errors[day]
            pct = count / total_errors * 100 if total_errors > 0 else 0
            if count > 0:
                print(f"   {day}: {count:2d} errors ({pct:4.1f}%)")
    
    def discover_month_position_patterns(self, problematic_cases):
        """Look for month start/end positioning patterns"""
        
        print(f"\n📍 MONTH POSITION PATTERN ANALYSIS:")
        
        start_errors = [case for case in problematic_cases if case['is_month_start']]
        end_errors = [case for case in problematic_cases if case['is_month_end']]
        middle_errors = [case for case in problematic_cases if not case['is_month_start'] and not case['is_month_end']]
        
        total = len(problematic_cases)
        print(f"\nMonth Start (days 1-5): {len(start_errors)} errors ({len(start_errors)/total*100:.1f}%)")
        print(f"Month End (last 5 days): {len(end_errors)} errors ({len(end_errors)/total*100:.1f}%)")  
        print(f"Month Middle: {len(middle_errors)} errors ({len(middle_errors)/total*100:.1f}%)")
        
        # Analyze specific day positions
        day_distribution = Counter(case['day'] for case in problematic_cases)
        
        print(f"\n🔢 Error Distribution by Day of Month:")
        for day_group in [(1, 5), (6, 10), (11, 15), (16, 20), (21, 25), (26, 31)]:
            start, end = day_group
            count = sum(day_distribution[d] for d in range(start, end+1))
            if count > 0:
                print(f"   Days {start:2d}-{end:2d}: {count:2d} errors")
    
    def discover_holiday_interaction_patterns(self, problematic_cases):
        """Look for holiday interaction patterns"""
        
        print(f"\n🏖️  HOLIDAY INTERACTION PATTERN ANALYSIS:")
        
        # Analyze cases near holidays
        holiday_adjacent_cases = []
        
        for case in problematic_cases:
            run_date = case['run_date']
            ca_holidays = holidays.Canada(years=run_date.year)
            
            # Check if run date or nearby dates are holidays
            is_holiday_adjacent = False
            holiday_info = []
            
            for offset in range(-3, 4):  # Check 3 days before/after
                check_date = run_date + timedelta(days=offset)
                if check_date in ca_holidays:
                    holiday_name = ca_holidays[check_date]
                    holiday_info.append(f"{holiday_name} (day{offset:+d})")
                    is_holiday_adjacent = True
            
            if is_holiday_adjacent:
                case_copy = case.copy()
                case_copy['holiday_info'] = holiday_info
                holiday_adjacent_cases.append(case_copy)
        
        print(f"\nHoliday-adjacent errors: {len(holiday_adjacent_cases)} ({len(holiday_adjacent_cases)/len(problematic_cases)*100:.1f}%)")
        
        if holiday_adjacent_cases:
            print(f"\n{'Date':<12} {'Offset':<7} {'Holiday Context'}")
            print(f"{'-'*12} {'-'*7} {'-'*30}")
            
            for case in holiday_adjacent_cases[:10]:  # Show first 10
                holidays_str = ', '.join(case['holiday_info'])
                print(f"{case['date']:<12} {case['offset']:<7} {holidays_str}")
        
        return holiday_adjacent_cases
    
    def suggest_new_algorithmic_rules(self, patterns_found):
        """Suggest new rules based on discovered patterns"""
        
        print(f"\n🎯 RECOMMENDED NEW ALGORITHMIC RULES:")
        
        christmas_problems, consecutive_clusters, holiday_adjacent = patterns_found
        
        if christmas_problems:
            print(f"\n🎄 Christmas Period Enhancement:")
            day_patterns = Counter(case['day'] for case in christmas_problems)
            most_problematic_days = [day for day, count in day_patterns.most_common(3)]
            
            print(f"   → Extend Christmas logic to cover days {most_problematic_days}")
            print(f"   → Current logic covers Dec 20+, consider Dec 15+ coverage")
        
        if consecutive_clusters:
            print(f"\n📅 Consecutive Clustering Rules:")
            for cluster in consecutive_clusters:
                if len(cluster) >= 3:  # Significant clusters
                    start_day = cluster[0]['day']
                    end_day = cluster[-1]['day']
                    month = cluster[0]['month']
                    year = cluster[0]['year']
                    
                    # Check if there's a consistent pattern
                    patterns = [(c['predicted'], c['ground_truth']) for c in cluster]
                    if len(set(patterns)) <= 2:  # Mostly consistent
                        sample = cluster[0]
                        print(f"   → {calendar.month_name[month]} days {start_day}-{end_day}: "
                              f"Consider rule pred={sample['ground_truth']} instead of {sample['predicted']}")
        
        if holiday_adjacent:
            unique_holidays = set()
            for case in holiday_adjacent:
                unique_holidays.update(case['holiday_info'])
            
            if len(unique_holidays) > 3:
                print(f"\n🏖️  Holiday Interaction Rules:")
                print(f"   → {len(unique_holidays)} different holiday contexts causing errors")
                print(f"   → Consider enhanced holiday cascade logic")


def main():
    """Main pattern discovery execution"""
    
    engine = PatternDiscoveryEngine()
    
    # Phase 1: Collect all problematic cases
    problematic_cases, all_cases = engine.analyze_remaining_problematic_cases()
    
    # Phase 2: Discover specific pattern types
    christmas_problems = engine.discover_christmas_patterns(problematic_cases)
    consecutive_clusters = engine.discover_consecutive_clustering_patterns(problematic_cases)
    
    # Phase 3: Analyze broader patterns
    engine.discover_seasonal_quarterly_patterns(problematic_cases)
    engine.discover_month_position_patterns(problematic_cases)
    holiday_adjacent = engine.discover_holiday_interaction_patterns(problematic_cases)
    
    # Phase 4: Generate actionable recommendations
    patterns_found = (christmas_problems, consecutive_clusters, holiday_adjacent)
    engine.suggest_new_algorithmic_rules(patterns_found)
    
    print(f"\n🔍 PATTERN DISCOVERY COMPLETE!")
    print(f"💡 Found systematic patterns in {len(problematic_cases)} remaining problematic cases")
    print(f"🎯 Ready to implement targeted fixes for newly discovered rule patterns")


if __name__ == "__main__":
    main()
