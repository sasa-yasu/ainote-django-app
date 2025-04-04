from django import template

register = template.Library()

@register.simple_tag
def get_fixed_value(key):
    values = {
        'MBTI_TEST_URL': 'https://www.16personalities.com/ja/%E6%80%A7%E6%A0%BC%E8%A8%BA%E6%96%AD%E3%83%86%E3%82%B9%E3%83%88',
        'TOP_GOOGLE_CALENDAR_MONTHLY': '<iframe src="https://calendar.google.com/calendar/embed?height=800&wkst=2&ctz=Asia%2FTokyo&showPrint=0&showTabs=0&title=All%20Events&mode=MONTH&src=c2FzYS55YXN1LnNpbkBnbWFpbC5jb20&src=OTUyZWE3ODM2MGMwMTcyYWU3MmM0ZjdjODIzZjFkZGQ4M2IwNWI1NDA4ZGE4Y2I1YTFjYmU3ZTkwNWQ1ZGMzOEBncm91cC5jYWxlbmRhci5nb29nbGUuY29t&src=amEuamFwYW5lc2UjaG9saWRheUBncm91cC52LmNhbGVuZGFyLmdvb2dsZS5jb20&color=%23039BE5&color=%23F09300&color=%230B8043" style="border-width:0" width="100%" height="800" frameborder="0" scrolling="no"></iframe>',
        'TOP_GOOGLE_CALENDAR_WEEKLY':  '<iframe src="https://calendar.google.com/calendar/embed?height=800&wkst=2&ctz=Asia%2FTokyo&showPrint=0&showTabs=0&title=All%20Events&mode=WEEK&src=c2FzYS55YXN1LnNpbkBnbWFpbC5jb20&src=OTUyZWE3ODM2MGMwMTcyYWU3MmM0ZjdjODIzZjFkZGQ4M2IwNWI1NDA4ZGE4Y2I1YTFjYmU3ZTkwNWQ1ZGMzOEBncm91cC5jYWxlbmRhci5nb29nbGUuY29t&src=amEuamFwYW5lc2UjaG9saWRheUBncm91cC52LmNhbGVuZGFyLmdvb2dsZS5jb20&color=%23039BE5&color=%23F09300&color=%230B8043" style="border-width:0" width="100%" height="800" frameborder="0" scrolling="no"></iframe>',
    }
    return values.get(key, '')
