import numpy as np
import statistics
from typing import List, Dict

def analyze_evaluation_scores(all_scores: List[Dict]):
    """
    Analyze evaluation scores with detailed statistics
    """
    # Sample evaluation scores for different metrics
    sample_scores = {
        "coherence": [23, 24, 22, 25, 15],  # Note: 15 is an outlier
        "relevance": [21, 22, 23, 22, 21],
        "helpfulness": [24, 23, 25, 24, 23],
        "context_awareness": [13, 14, 13, 14, 8],  # Note: 8 is an outlier
        "consistency": [9, 8, 9, 8, 9]
    }
    
    results = {}
    all_variances = []
    
    for metric, scores in sample_scores.items():
        # 1. IQR Analysis
        q1 = np.percentile(scores, 25)
        q3 = np.percentile(scores, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Filter outliers
        filtered_scores = [
            s for s in scores 
            if lower_bound <= s <= upper_bound
        ]
        
        # 2. Calculate Variance
        variance = statistics.variance(filtered_scores) if len(filtered_scores) > 1 else 0
        all_variances.append(variance)
        
        results[metric] = {
            "original_scores": scores,
            "filtered_scores": filtered_scores,
            "quartiles": {
                "q1": q1,
                "q3": q3,
                "iqr": iqr
            },
            "bounds": {
                "lower": lower_bound,
                "upper": upper_bound
            },
            "statistics": {
                "median": statistics.median(filtered_scores),
                "variance": variance
            }
        }
    
    # 3. Calculate Overall Confidence
    avg_variance = statistics.mean(all_variances)
    confidence = 1 / (1 + avg_variance)
    
    results["overall"] = {
        "average_variance": avg_variance,
        "confidence_score": round(confidence, 2)
    }
    
    return results

# Example usage and output formatting
def print_analysis(analysis):
    print("Evaluation Analysis:")
    print("-" * 50)
    
    for metric, data in analysis.items():
        if metric != "overall":
            print(f"\n{metric.upper()}:")
            print(f"Original scores: {data['original_scores']}")
            print(f"Filtered scores: {data['filtered_scores']}")
            print(f"Median score: {data['statistics']['median']}")
            print(f"Variance: {data['statistics']['variance']:.2f}")
            
    print("\nOVERALL METRICS:")
    print(f"Average Variance: {analysis['overall']['average_variance']:.2f}")
    print(f"Confidence Score: {analysis['overall']['confidence_score']}")

# Run analysis
analysis = analyze_evaluation_scores([])
print_analysis(analysis)