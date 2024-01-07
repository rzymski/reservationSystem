from django import template
from django.utils import formats

register = template.Library()


@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})


polishMonths = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']


@register.filter(name='myDateFormat')
def myDateFormat(value):
    year = value.strftime("%Y")
    monthNumber = int(value.strftime("%m"))
    month = polishMonths[monthNumber-1]
    day = value.strftime("%d").lstrip("0")
    hour = value.strftime("%H").lstrip("0")
    minute = value.strftime("%M")
    return f"{day} {month} {year}"


@register.filter(name='myTimeFormat')
def myTimeFormat(value):
    hour = value.strftime("%H").lstrip("0")
    minute = value.strftime("%M")
    return f"{hour}:{minute}"

# @register.filter(name='myDateFormat')
# def myDateFormat(value):
#     year = value.strftime("%Y")
#     monthNumber = int(value.strftime("%m"))
#     month = polishMonths[monthNumber-1]
#     day = value.strftime("%d").lstrip("0")
#     hour = value.strftime("%H").lstrip("0")
#     minute = value.strftime("%M")
#     return f"{hour}:{minute} {day} {month} {year}"
#    #return formats.date_format(value, "d F Y H:i")
