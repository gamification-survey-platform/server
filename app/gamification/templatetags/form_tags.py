from django import template

register = template.Library()


@register.filter
def field_type(bound_field):
    return bound_field.field.widget.__class__.__name__


@register.filter
def input_class(bound_field):
    field_class = field_type(bound_field)

    css_class = ''
    if field_class == 'CheckboxInput':
        css_class += 'form-check-input'
    elif field_class == 'DateTimeInput':
        css_class += 'form-control datetimepicker'
    elif field_class == 'DateInput':
        css_class += 'form-control datepicker'
    else:
        css_class += 'form-control'

    if bound_field.form.is_bound:
        if bound_field.errors:
            css_class += ' is-invalid'
        elif field_type(bound_field) != 'PasswordInput':
            css_class += ' is-valid'

    return css_class


@register.filter
def input_style(bound_field):
    field_class = field_type(bound_field)

    css_style = ''
    if field_class != 'CheckboxInput':
        css_style += 'height: auto; padding: 0.375rem 0.75rem;'
    if field_class == 'Select':
        css_style += ' color: #212529;'

    return css_style
