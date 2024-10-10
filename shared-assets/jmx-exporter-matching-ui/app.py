from flask import Flask, render_template, request, jsonify
import re
import yaml

app = Flask(__name__)

def transform_pattern(pattern):
    """
    Transform the pattern from the YAML rule into a valid regular expression
    for matching the metric.

    - Replace the first '<' with ':'
    - Remove any occurrences of '<>' entirely.
    - Remove any occurrences of '<>(.+)' entirely.
    - Remove any other angle brackets.
    """
    # Remove occurrences of '<>(...)'
    transformed_pattern = re.sub(r'<>(.+)', '', pattern)

    # Remove all occurrences of '<>'
    transformed_pattern = transformed_pattern.replace('<>', '')

    # Replace the first occurrence of '<' with ':'
    transformed_pattern = transformed_pattern.replace('<', ':', 1)

    # Remove all other occurrences of '>'
    transformed_pattern = transformed_pattern.replace('>', '')

    # Escape dots in the pattern for regex, except inside capturing groups
    transformed_pattern = re.sub(r'(?<!\()\.(?!\))', r'\\.', transformed_pattern)

    # Convert '*' to '.*' for regex matching
    transformed_pattern = transformed_pattern.replace('*', '.*')

    # Remove any whitespace
    transformed_pattern = re.sub(r'\s+', '', transformed_pattern)

    return transformed_pattern

def match_metric_to_rule(metric, rule_pattern):
    """
    Check if the given metric matches the rule pattern.
    """
    # Transform the rule pattern into a regular expression
    regex_pattern = transform_pattern(rule_pattern)

    print(f"Regex Pattern: {regex_pattern}")

    match = re.match(regex_pattern, metric)

    return bool(match)

def evaluate_metric(yaml_content, metric):
    """
    Evaluate the given metric against the rules and whitelist/blacklist
    in the provided YAML content.
    """
    try:
        config = yaml.safe_load(yaml_content)

        # Check if the metric is in the blacklist
        for blacklist_pattern in config.get('blacklistObjectNames', []):
            if re.match(blacklist_pattern.replace('*', '.*'), metric):
                return "Metric is blacklisted."

        # If whitelistObjectNames is present, check the whitelist
        whitelist = config.get('whitelistObjectNames', None)
        if whitelist:
            whitelisted = False
            for whitelist_pattern in whitelist:
                if re.match(whitelist_pattern.replace('*', '.*'), metric):
                    whitelisted = True
                    break

            if not whitelisted:
                return "Metric is not whitelisted."

        # If whitelistObjectNames is not present, skip whitelist check

        # Check the metric against the rules
        for rule in config.get('rules', []):
            if match_metric_to_rule(metric, rule['pattern']):
                return "Metric matches the rule!"

        return "Metric did not match any rule."

    except Exception as e:
        return f"Error processing YAML or metric: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    yaml_content = data.get('yaml')
    metric = data.get('metric')

    result = evaluate_metric(yaml_content, metric)

    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)