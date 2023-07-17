def format_template(template: str, params: dict) -> str:
    def handle_quotes(value):
        """Add single quotes to a string if not already present"""
        return f"'{value}'" if isinstance(value, str) and not value.startswith("'") and not value.endswith("'") else value

    # SQL style
    for key, value in params.items():
        value = handle_quotes(value)
        template = template.replace(':' + key, str(value))

    # Double-brace style
    for key, value in params.items():
        value = handle_quotes(value)
        template = template.replace('{{' + key + '}}', str(value))

    # Dollar sign style
    for key, value in params.items():
        value = handle_quotes(value)
        template = template.replace('$' + key, str(value))

    # Python style
    template = template.format(**params)

    return template
