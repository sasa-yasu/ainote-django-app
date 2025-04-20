from django.utils.safestring import mark_safe
from django import forms
from .models import Headline

class HeadlineForm(forms.ModelForm):

    images = forms.ImageField(
        label='Images', widget=forms.FileInput(attrs={}),
        required=True, help_text='* Image file size will be adjusted to max 1500px X 1500px, and ratio 23:9.'
    )
    title = forms.CharField(
        label='Title', max_length=100, widget=forms.TextInput(attrs={}),
        required=True, help_text='* Title should be max 100 characters.'
    )
    period = forms.CharField(
        label='Period', max_length=100, widget=forms.TextInput(attrs={}),
        required=False, help_text='* Period should be max 100 characters.'
    )
    overview = forms.CharField(
        label='Overview', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Brief explanation.'
    )
    context = forms.CharField(
        label='Context', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Shorter is better.'
    )
    published_at = forms.DateField(
        label='Published at', widget=forms.DateInput(attrs={'type': 'date'}), input_formats=['%Y-%m-%d'],
        required=False, help_text='* When you want to appear. Cover page will order-by Headlines by this date.'
        )
    remarks = forms.CharField(
        label='Remarks', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Anything you want to share.'
    )

    class Meta:
        model = Headline
        fields = ("images", "title", "period", "overview", "context", "published_at", "remarks")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.TextInput, forms.PasswordInput, forms.Select, forms.Textarea, forms.DateInput, forms.FileInput, forms.EmailField)):
                widget.attrs.setdefault('class', 'form-control')
            if isinstance(widget, (forms.RadioSelect, forms.CheckboxSelectMultiple)):
                widget.attrs.setdefault('class', 'form-check-input')

            if field.required:
                field.label = mark_safe(f"{field.label} <span style='color: red; font-size:10pt;'>(*)</span>") # if required field, show "(*)"
