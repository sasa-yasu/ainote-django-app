from django import template

register = template.Library()

@register.simple_tag
def get_fixed_value(key):
    values = {
        'MBTI_TEST_URL': 'https://www.16personalities.com/ja/%E6%80%A7%E6%A0%BC%E8%A8%BA%E6%96%AD%E3%83%86%E3%82%B9%E3%83%88',
    }
    return values.get(key, '')
