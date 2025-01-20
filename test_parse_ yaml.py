import yaml

def parse_yaml_file(filename):
    with open(filename, 'r') as yaml_file:
        parsed_yaml = yaml.safe_load(yaml_file)
    return parsed_yaml

if __name__ == "__main__":
    yaml_file = "config.yaml"
    parsed_data = parse_yaml_file(yaml_file)
    
    # Accessing variables from the parsed YAML data
    string_var = parsed_data.get('string_var')
    integer_var = parsed_data.get('integer_var')
    float_var = parsed_data.get('float_var')
    boolean_var = parsed_data.get('boolean_var')
    list_var = parsed_data.get('list_var')
    dictionary_var = parsed_data.get('dictionary_var')
    
    # Printing out the parsed variables
    print(f"String variable: {string_var}")
    print(f"Integer variable: {integer_var}")
    print(f"Float variable: {float_var}")
    print(f"Boolean variable: {boolean_var}")
    print(f"List variable: {list_var}")
    print(f"Dictionary variable: {dictionary_var}")
