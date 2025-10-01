#!/usr/bin/env python3
"""
Comprehensive Cluster Analyzer - All Error Types
Identifies consecutive clusters for 1-day, 2-day, and 3+ day offsets
Prioritizes by confidence and probable positive impact for surgical fixes
"""

import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import calendar
import holidays
from payment_schedule_generator import Table109Generator
from rapid_test_framework import RapidTester


class ComprehensiveClusterAnalyzer(RapidTester):
    """Comprehensive analyzer for all error offset types"""
    
    def __init__(self):
        super().__init__()
        self.generator_cache = {}
        
    def get_generator(self, year):
        if year not in self.generator_cache:
            self.generator_cache[year] = Table109Generator(year)
        return self.generator_cache[year]
    
    def collect_all_error_cases(self):
        """Collect all error cases categorized by offset"""
        
        print("🔍 COMPREHENSIVE CLUSTER ANALYZER")
        print("="*60)
        
        error_cases = {
            '1-day': [],
            '2-day': [], 
            '3+day': []
        }
        
        for (year, month), month_data in self.ground_truth.items():
            generator = self.get_generator(year)
            
            for day, gt_payment in month_data.items():
                run_date = datetime(year, month, day)
                
                try:
                    predicted_payment = generator.calculate_payment_date(run_date)
                    diff = abs(predicted_payment - gt_payment)
                    
                    if diff == 0:
                        continue  # Perfect matches, not interested
                    
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
                    }
                    
                    if diff == 1:
                        error_cases['1-day'].append(case_info)
                    elif diff == 2:
                        error_cases['2-day'].append(case_info)
                    elif diff >= 3:
                        error_cases['3+day'].append(case_info)
                
                except Exception as e:
                    print(f"Error analyzing {year}-{month:02d}-{day:02d}: {e}")
        
        print(f"\n📊 ERROR BREAKDOWN (FULL DATASET):")
        for error_type, cases in error_cases.items():
            print(f"{error_type:<8}: {len(cases):3d} cases")
        
        total_errors = sum(len(cases) for cases in error_cases.values())
        print(f"Total errors: {total_errors} out of {total_errors + sum(1 for (year, month), month_data in self.ground_truth.items() for day, gt_payment in month_data.items())} cases")
        
        return error_cases
    
    def find_consecutive_clusters(self, error_cases):
        """Find consecutive day clusters for each error type"""
        
        all_clusters = {}
        
        for error_type, cases in error_cases.items():
            print(f"\n🔍 ANALYZING {error_type.upper()} CONSECUTIVE CLUSTERS:")
            
            # Group by year-month
            month_groups = defaultdict(list)
            for case in cases:
                key = f"{case['year']}-{case['month']:02d}"
                month_groups[key].append(case)
            
            clusters = []
            
            for month_key, month_cases in month_groups.items():
                if len(month_cases) >= 2:
                    month_cases.sort(key=lambda x: x['day'])
                    
                    # Find consecutive sequences
                    current_cluster = [month_cases[0]]
                    
                    for i in range(1, len(month_cases)):
                        if month_cases[i]['day'] == month_cases[i-1]['day'] + 1:
                            current_cluster.append(month_cases[i])
                        else:
                            if len(current_cluster) >= 2:  # At least 2 consecutive days
                                clusters.append(current_cluster.copy())
                            current_cluster = [month_cases[i]]
                    
                    if len(current_cluster) >= 2:
                        clusters.append(current_cluster)
            
            # Sort clusters by length (longer = higher confidence)
            clusters.sort(key=len, reverse=True)
            
            print(f"Found {len(clusters)} consecutive clusters for {error_type}")
            
            # Show top clusters
            for i, cluster in enumerate(clusters[:10]):  # Top 10
                if len(cluster) >= 2:
                    start_day = cluster[0]['day']
                    end_day = cluster[-1]['day']
                    month = cluster[0]['month']
                    year = cluster[0]['year']
                    
                    # Check direction consistency
                    directions = [case['direction'] for case in cluster]
                    consistent_direction = len(set(directions)) == 1
                    
                    month_name = calendar.month_name[month]
                    confidence = "HIGH" if len(cluster) >= 4 and consistent_direction else "MED"
                    
                    print(f"   #{i+1}: {month_name} {year}, days {start_day}-{end_day} "
                          f"({len(cluster)} days, {confidence} confidence)")
                    
                    if consistent_direction:
                        print(f"        Consistent {directions[0]} direction")
                    else:
                        print(f"        Mixed directions: {set(directions)}")
            
            all_clusters[error_type] = clusters
        
        return all_clusters
    
    def prioritize_clusters_for_surgery(self, all_clusters):
        """Prioritize clusters by confidence and probable impact"""
        
        print(f"\n🎯 PRIORITIZED SURGICAL TARGETS:")
        print(f"Ranked by: Length × Consistency × Error Type Impact")
        
        surgical_targets = []
        
        # Weight by error type (1-day errors easier to fix, 3+ day harder but higher impact)
        error_weights = {'1-day': 1.0, '2-day': 1.5, '3+day': 2.0}
        
        for error_type, clusters in all_clusters.items():
            for cluster in clusters:
                if len(cluster) >= 2:  # At least 2 consecutive days
                    
                    # Calculate confidence score
                    length_score = len(cluster)  # Longer = more confident
                    
                    directions = [case['direction'] for case in cluster]
                    consistency_score = 2.0 if len(set(directions)) == 1 else 0.5
                    
                    error_impact = error_weights[error_type]
                    
                    total_score = length_score * consistency_score * error_impact
                    
                    surgical_targets.append({
                        'cluster': cluster,
                        'error_type': error_type,
                        'score': total_score,
                        'length': len(cluster),
                        'consistency': len(set(directions)) == 1,
                        'year': cluster[0]['year'],
                        'month': cluster[0]['month'],
                        'start_day': cluster[0]['day'],
                        'end_day': cluster[-1]['day']
                    })
        
        # Sort by score (highest first)
        surgical_targets.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\nTOP 15 SURGICAL TARGETS:")
        print(f"{'#':<3} {'Type':<6} {'Year-Month':<10} {'Days':<10} {'Len':<4} {'Cons':<5} {'Score':<6}")
        print(f"{'-'*3} {'-'*6} {'-'*10} {'-'*10} {'-'*4} {'-'*5} {'-'*6}")
        
        for i, target in enumerate(surgical_targets[:15]):
            month_name = calendar.month_name[target['month']][:3]
            days_range = f"{target['start_day']}-{target['end_day']}"
            year_month = f"{target['year']}-{month_name}"
            consistency = "YES" if target['consistency'] else "NO"
            
            print(f"{i+1:<3} {target['error_type']:<6} {year_month:<10} {days_range:<10} "
                  f"{target['length']:<4} {consistency:<5} {target['score']:<6.1f}")
        
        return surgical_targets


def main():
    """Main comprehensive cluster analysis execution"""
    
    analyzer = ComprehensiveClusterAnalyzer()
    
    # Phase 1: Collect all error cases
    error_cases = analyzer.collect_all_error_cases()
    
    # Phase 2: Find consecutive clusters
    all_clusters = analyzer.find_consecutive_clusters(error_cases)
    
    # Phase 3: Prioritize for surgical implementation
    surgical_targets = analyzer.prioritize_clusters_for_surgery(all_clusters)
    
    print(f"\n🎯 READY FOR SYSTEMATIC SURGICAL IMPLEMENTATION!")
    print(f"Total targets identified: {len(surgical_targets)}")
    print(f"Will implement highest-scoring targets one by one with testing.")
    
    return surgical_targets


if __name__ == "__main__":
    surgical_targets = main()
