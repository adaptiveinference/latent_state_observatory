# CHECK_TOKEN: PYC099

# Function to render a simple template with a given context
def simple_template_render(template, context):
    # Check if the template is a valid Python string
    if not isinstance(template, str):
        raise ValueError("Template must be a string")
    
    # Check if the context is a dictionary
    if not isinstance(context, dict):
        raise ValueError("Context must be a dictionary")
    
    # Check if the context has a 'name' key
    if 'name' not in context:
        raise ValueError("Context must have a 'name' key")
    
    # Render the template with the context
    rendered_template = template.format(**context)
    
    return rendered_template

# Example usage
template = """
{{name}}
"""

context = {
    "name": "John"
}

rendered_template = simple_template_render(template, context)
print(rendered_template)  # Output: John

# Explanation:
- The `simple_template_render` function takes two arguments: `template` and `context`.
- The first argument `template` is a string that represents the template to be rendered. It should contain placeholders for variables that will be replaced with values from the `context` dictionary.
- The second argument `context` is a dictionary that represents the variables and their values to be used in the template. The `name` key in the `context` dictionary should contain the name of the variable to be replaced.
- The function first checks if the `template` is a string. If it's not, it raises a `ValueError` with the message "Template must be a string".
- Next, it checks if the `context` is a dictionary. If it's not, it raises a `ValueError` with the message "Context must be a dictionary".
- The function then checks if the `context` has a 'name' key. If it doesn't, it raises a `ValueError` with the message "Context must have a 'name' key".
- If all the checks pass, the function uses the `format` method to replace the placeholders in the `template` with the values from the `context` dictionary.
- Finally, the function returns the rendered template as a string.

In the example usage, we define a template string `{{name}}` and a dictionary `context` with a 'name' key containing the value "John". We then call the `simple_template