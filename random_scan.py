import random

def random_value_in_range(range_string):
    """Generate a random value within the given range with 2 decimal places."""
    if '-' in range_string:
        lower, upper = range_string.split('-')
        value = random.uniform(float(lower.strip()), float(upper.strip()))
    elif '<' in range_string:
        upper = float(range_string.strip('<').strip())
        value = random.uniform(0, upper)
    elif '>' in range_string:
        lower = float(range_string.strip('>').strip())
        value = random.uniform(lower, lower * 2)  # Example logic
    else:
        value = float(range_string)
    return round(value, 2)

# Metabolite data (you can add more metabolites as needed)
diabetes_metabolites = {
    'Creatinine': ('53 - 106', '107 - 212', '213 - 442'),
    'Glucose': ('4.0 - 5.5', '5.5 - 6.9', '>7.2'),
    'HDL Cholesterol': ('>1.04', '1.04 - 1.55', '<1.04')
}

diabetes_obesity_metabolites = {
    'Albumin': ('40 - 55', '35 - 50', '<35'),
    'ALT': ('<40', '0 - 40', '>40'),
    'AST': ('<40', '0 - 40', '>40')
}

# Function to generate random scan
def generate_random_scan():
    scan_results = {}
    for metabolite, ranges in diabetes_metabolites.items():
        scan_results[metabolite] = random_value_in_range(random.choice(ranges))
    for metabolite, ranges in diabetes_obesity_metabolites.items():
        scan_results[metabolite] = random_value_in_range(random.choice(ranges))
    return scan_results

# Generate and print the random scan
random_scan = generate_random_scan()
print(random_scan)
