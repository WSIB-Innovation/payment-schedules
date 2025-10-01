#!/usr/bin/env python3
"""
1-Day Offset Pattern Analyzer
Specialized analyzer for the 370 cases with 1-day offset (15.8% of all cases)
Looking for patterns to convert these to perfect matches
"""

import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import calendar
import holidays
from payment_schedule_generator import Table109Generator
from rapid_test_framework import RapidTester


class OneDayPatternAnalyzer(RapidTester):
    """Specialized analyzer for 1-day offset cases"""
    
    def __init__(self):
        super().__init__()
        self.generator_cache = {}
        
    def get_generator(self, year):
        if year not in self.generator_cache:
            self.generator_cache[year] = Table109Generator(year)
        return self.generator_cache[year]
    
    def collect_oneday_cases(self):
        """Collect all 1-day offset cases for analysis"""
        
        print("🔍 1-DAY OFFSET PATTERN ANALYZER")
        print("="*60)
        print("Target: Convert 370 one-day errors to perfect matches")
        
        oneday_cases = []
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
                        'direction': '+1' if predicted_payment > gt_payment else '-1',
                        'weekday': run_date.strftime('%A'),
                        'weekday_num': run_date.weekday(),
                        'is_month_start': day <= 5,
                        'is_month_end': day >= calendar.monthrange(year, month)[1] - 4,
                        'quarter': (month - 1) // 3 + 1,
                        'period': self._get_period(year, month, day)
                    }
                    
                    all_cases.append(case_info)
                    
                    if diff == 1:  # Exactly 1-day offset
                        oneday_cases.append(case_info)
                
                except Exception as e:
                    print(f"Error analyzing {year}-{month:02d}-{day:02d}: {e}")
        
        print(f"\n📊 OVERVIEW:")
        print(f"Total cases: {len(all_cases):,}")
        print(f"1-day offset cases: {len(oneday_cases)} ({len(oneday_cases)/len(all_cases)*100:.1f}%)")
        
        return oneday_cases
    
    def analyze_direction_patterns(self, oneday_cases):
        """Analyze if errors are consistently +1 or -1"""
        
        print(f"\n🎯 DIRECTION ANALYSIS (Predicted vs Actual):")
        
        plus_one_cases = [case for case in oneday_cases if case['direction'] == '+1']
        minus_one_cases = [case for case in oneday_cases if case['direction'] == '-1']
        
        print(f"Predicted too high (+1): {len(plus_one_cases)} cases ({len(plus_one_cases)/len(oneday_cases)*100:.1f}%)")
        print(f"Predicted too low (-1):  {len(minus_one_cases)} cases ({len(minus_one_cases)/len(oneday_cases)*100:.1f}%)")
        
        # Analyze patterns in each direction
        if plus_one_cases:
            print(f"\n📈 OVER-PREDICTION (+1) PATTERNS:")
            self._analyze_subset_patterns(plus_one_cases, "Over-predictions")
        
        if minus_one_cases:
            print(f"\n📉 UNDER-PREDICTION (-1) PATTERNS:")
            self._analyze_subset_patterns(minus_one_cases, "Under-predictions")
        
        return plus_one_cases, minus_one_cases
    
    def _analyze_subset_patterns(self, cases, label):
        """Analyze patterns within a subset of cases"""
        
        # Weekday patterns
        weekday_counts = Counter(case['weekday'] for case in cases)
        print(f"   Top weekdays: {dict(weekday_counts.most_common(3))}")
        
        # Month patterns  
        month_counts = Counter(case['month'] for case in cases)
        month_names = {m: calendar.month_name[m][:3] for m in month_counts.keys()}
        top_months = [(month_names[m], count) for m, count in month_counts.most_common(3)]
        print(f"   Top months: {dict(top_months)}")
        
        # Day of month patterns
        day_counts = Counter(case['day'] for case in cases)
        print(f"   Top days: {dict(day_counts.most_common(5))}")
    
    def analyze_holiday_patterns(self, oneday_cases):
        """Detailed holiday proximity analysis"""
        
        print(f"\n🏖️  1-DAY OFFSET HOLIDAY ANALYSIS:")
        
        holiday_adjacent_cases = []
        holiday_contexts = defaultdict(list)
        
        for case in oneday_cases:
            run_date = case['run_date']
            ca_holidays = holidays.Canada(years=run_date.year)
            
            # Check holiday proximity (3 days before/after)
            holiday_info = []
            is_holiday_adjacent = False
            
            for offset in range(-3, 4):
                check_date = run_date + timedelta(days=offset)
                if check_date in ca_holidays:
                    holiday_name = ca_holidays[check_date]
                    holiday_info.append((holiday_name, offset))
                    is_holiday_adjacent = True
                    
                    # Track specific holiday contexts
                    context_key = f"{holiday_name}_day{offset:+d}"
                    holiday_contexts[context_key].append(case)
            
            if is_holiday_adjacent:
                case_copy = case.copy()
                case_copy['holiday_info'] = holiday_info
                holiday_adjacent_cases.append(case_copy)
        
        print(f"Holiday-adjacent 1-day errors: {len(holiday_adjacent_cases)} ({len(holiday_adjacent_cases)/len(oneday_cases)*100:.1f}%)")
        
        # Find most common holiday contexts
        print(f"\n🔍 TOP HOLIDAY CONTEXTS:")
        holiday_context_counts = {k: len(v) for k, v in holiday_contexts.items()}
        top_contexts = sorted(holiday_context_counts.items(), key=lambda x: x[1], reverse=True)
        
        for context, count in top_contexts[:10]:
            if count >= 2:  # Only show contexts with multiple cases
                print(f"   {context}: {count} cases")
                
                # Show pattern for this context
                context_cases = holiday_contexts[context]
                directions = [case['direction'] for case in context_cases]
                direction_counts = Counter(directions)
                
                if len(direction_counts) == 1:
                    consistent_direction = list(direction_counts.keys())[0]
                    print(f"      → Consistent {consistent_direction} error pattern")
                else:
                    print(f"      → Mixed directions: {dict(direction_counts)}")
        
        return holiday_adjacent_cases, holiday_contexts
    
    def analyze_weekday_patterns(self, oneday_cases):
        """Deep dive into weekday patterns for 1-day errors"""
        
        print(f"\n📅 1-DAY OFFSET WEEKDAY DEEP ANALYSIS:")
        
        weekday_analysis = {}
        
        for day_name in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            day_cases = [case for case in oneday_cases if case['weekday'] == day_name]
            
            if day_cases:
                # Direction analysis
                directions = Counter(case['direction'] for case in day_cases)
                
                # Period analysis
                periods = Counter(case['period'] for case in day_cases)
                
                # Month position analysis
                positions = []
                for case in day_cases:
                    if case['is_month_start']:
                        positions.append('start')
                    elif case['is_month_end']:
                        positions.append('end')  
                    else:
                        positions.append('middle')
                position_counts = Counter(positions)
                
                weekday_analysis[day_name] = {
                    'count': len(day_cases),
                    'directions': dict(directions),
                    'periods': dict(periods),
                    'positions': dict(position_counts)
                }
        
        # Display analysis
        for day_name, analysis in weekday_analysis.items():
            if analysis['count'] > 0:
                print(f"\n   {day_name}: {analysis['count']} cases")
                print(f"      Directions: {analysis['directions']}")
                if len(analysis['periods']) <= 3:
                    print(f"      Periods: {analysis['periods']}")
                if len(analysis['positions']) <= 3:
                    print(f"      Positions: {analysis['positions']}")
        
        return weekday_analysis
    
    def analyze_consecutive_patterns(self, oneday_cases):
        """Look for consecutive day patterns in 1-day errors"""
        
        print(f"\n📅 1-DAY CONSECUTIVE PATTERN ANALYSIS:")
        
        # Group by year-month
        month_groups = defaultdict(list)
        for case in oneday_cases:
            key = f"{case['year']}-{case['month']:02d}"
            month_groups[key].append(case)
        
        consecutive_clusters = []
        
        for month_key, cases in month_groups.items():
            if len(cases) >= 2:
                cases.sort(key=lambda x: x['day'])
                
                # Find consecutive sequences
                current_cluster = [cases[0]]
                
                for i in range(1, len(cases)):
                    if cases[i]['day'] == cases[i-1]['day'] + 1:
                        current_cluster.append(cases[i])
                    else:
                        if len(current_cluster) >= 2:
                            consecutive_clusters.append(current_cluster.copy())
                        current_cluster = [cases[i]]
                
                if len(current_cluster) >= 2:
                    consecutive_clusters.append(current_cluster)
        
        print(f"Found {len(consecutive_clusters)} consecutive 1-day error clusters:")
        
        significant_clusters = []
        for cluster in consecutive_clusters:
            if len(cluster) >= 2:
                start_day = cluster[0]['day']
                end_day = cluster[-1]['day']
                month = cluster[0]['month']
                year = cluster[0]['year']
                
                month_name = calendar.month_name[month]
                print(f"\n   {month_name} {year}, days {start_day}-{end_day} ({len(cluster)} consecutive)")
                
                # Analyze consistency
                directions = [case['direction'] for case in cluster]
                predictions = [case['predicted'] for case in cluster]
                actuals = [case['ground_truth'] for case in cluster]
                
                if len(set(directions)) == 1:
                    print(f"      Consistent direction: {directions[0]}")
                    significant_clusters.append(cluster)
                else:
                    print(f"      Mixed directions: {set(directions)}")
                
                print(f"      Pattern: pred={predictions} vs actual={actuals}")
        
        return significant_clusters
    
    def suggest_oneday_fixes(self, analysis_results):
        """Suggest targeted fixes for 1-day patterns"""
        
        oneday_cases, (plus_one, minus_one), (holiday_adjacent, holiday_contexts), weekday_analysis, consecutive_clusters = analysis_results
        
        print(f"\n🎯 RECOMMENDED 1-DAY OFFSET FIXES:")
        
        # Direction-based fixes
        if len(plus_one) > len(minus_one) * 2:  # Significantly more over-predictions
            print(f"\n📈 SYSTEMATIC OVER-PREDICTION FIX:")
            print(f"   → {len(plus_one)} over-predictions vs {len(minus_one)} under-predictions")
            print(f"   → Consider systematic -1 day adjustment for specific patterns")
        elif len(minus_one) > len(plus_one) * 2:  # Significantly more under-predictions
            print(f"\n📉 SYSTEMATIC UNDER-PREDICTION FIX:")
            print(f"   → {len(minus_one)} under-predictions vs {len(plus_one)} over-predictions")
            print(f"   → Consider systematic +1 day adjustment for specific patterns")
        
        # Weekday-specific fixes
        weekday_counts = {day: data['count'] for day, data in weekday_analysis.items() if data['count'] > 0}
        if weekday_counts:
            max_weekday = max(weekday_counts.items(), key=lambda x: x[1])
            if max_weekday[1] > 30:  # Significant weekday bias
                print(f"\n📅 WEEKDAY-SPECIFIC FIX:")
                print(f"   → {max_weekday[0]} has {max_weekday[1]} 1-day errors (most problematic)")
                day_analysis = weekday_analysis[max_weekday[0]]
                if len(day_analysis['directions']) == 1:
                    direction = list(day_analysis['directions'].keys())[0]
                    print(f"   → Consistent {direction} direction - apply systematic correction")
        
        # Holiday-specific fixes
        top_holiday_contexts = sorted(holiday_contexts.items(), key=lambda x: len(x[1]), reverse=True)
        for context, cases in top_holiday_contexts[:3]:
            if len(cases) >= 3:  # Significant holiday pattern
                directions = [case['direction'] for case in cases]
                if len(set(directions)) == 1:  # Consistent direction
                    print(f"\n🏖️  HOLIDAY-SPECIFIC FIX:")
                    print(f"   → {context}: {len(cases)} cases, consistent {directions[0]} direction")
        
        # Consecutive cluster fixes
        if consecutive_clusters:
            print(f"\n📅 CONSECUTIVE PATTERN FIXES:")
            for cluster in consecutive_clusters:
                if len(cluster) >= 3:
                    start_day = cluster[0]['day']
                    end_day = cluster[-1]['day']
                    month = cluster[0]['month']
                    year = cluster[0]['year']
                    direction = cluster[0]['direction']  # Already verified consistent
                    
                    month_name = calendar.month_name[month]
                    print(f"   → {month_name} {year} days {start_day}-{end_day}: apply {direction} correction")


def main():
    """Main 1-day pattern analysis execution"""
    
    analyzer = OneDayPatternAnalyzer()
    
    # Phase 1: Collect 1-day offset cases
    oneday_cases = analyzer.collect_oneday_cases()
    
    # Phase 2: Analyze direction patterns (+1 vs -1)
    plus_one, minus_one = analyzer.analyze_direction_patterns(oneday_cases)
    
    # Phase 3: Holiday proximity analysis
    holiday_adjacent, holiday_contexts = analyzer.analyze_holiday_patterns(oneday_cases)
    
    # Phase 4: Weekday pattern analysis
    weekday_analysis = analyzer.analyze_weekday_patterns(oneday_cases)
    
    # Phase 5: Consecutive pattern analysis
    consecutive_clusters = analyzer.analyze_consecutive_patterns(oneday_cases)
    
    # Phase 6: Generate actionable recommendations
    analysis_results = (oneday_cases, (plus_one, minus_one), (holiday_adjacent, holiday_contexts), weekday_analysis, consecutive_clusters)
    analyzer.suggest_oneday_fixes(analysis_results)
    
    print(f"\n🔍 1-DAY PATTERN ANALYSIS COMPLETE!")
    print(f"💡 Analyzed {len(oneday_cases)} cases for systematic 1-day offset patterns")
    print(f"🎯 Ready to implement fixes to convert 1-day errors to perfect matches")


if __name__ == "__main__":
    main()
