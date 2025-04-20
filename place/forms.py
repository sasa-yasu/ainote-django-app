from django.utils.safestring import mark_safe
from django import forms
from .models import Place

class PlaceForm(forms.ModelForm):

    place = forms.CharField(
        label='Place', max_length=100, widget=forms.TextInput(attrs={}),
        required=True, help_text='* Place should be max 100 characters.'
        )
    images = forms.ImageField(
        label='Images', widget=forms.FileInput(attrs={}),
        required=False, help_text='* Place icon.'
        )
    delete_images_flg = forms.BooleanField(required=False, label='Delete Images')
    themes = forms.ImageField(
        label='Themes', widget=forms.FileInput(attrs={}),
        required=False, help_text='* Place theme in profile page.'
        )
    delete_themes_flg = forms.BooleanField(required=False, label='Delete Themes')
    area = forms.CharField(
        label='Area', max_length=100, widget=forms.TextInput(attrs={}),
        required=False, help_text='* Area should be max 100 characters.'
        )
    overview = forms.CharField(
        label='Overview', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Brief explanation.'
        )
    address = forms.CharField(
        label='Address', max_length=255, widget=forms.TextInput(attrs={}),
        required=False, help_text='* Address should be max 255 characters.'
        )
    tel = forms.CharField(
        label='Tel', max_length=100, widget=forms.TextInput(attrs={}),
        required=False, help_text='* Tel should be max 100 characters.'
        )
    url = forms.CharField(
        label='URL', max_length=500, widget=forms.TextInput(attrs={}),
        required=False, help_text='* URL should be max 500 characters.'
        )
    context = forms.CharField(
        label='Context', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Shorter is better.'
        )
    remarks = forms.CharField(
        label='Remarks', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Anything you want to share.'
        )
    schedule_monthly = forms.URLField(
        label='Schedule Monthly', max_length=1028, widget=forms.TextInput(attrs={}),
        required=False, help_text=mark_safe('* Past the google schedule monthly URL (start with "iframe" tag).<br/>* Should change width-setting to width="100%".')
    )
    schedule_weekly = forms.URLField(
        label='Schedule Weekly', max_length=1028, widget=forms.TextInput(attrs={}),
        required=False, help_text=mark_safe('* Past the google schedule weekly URL (start with "iframe" tag).<br/>* Should change width-setting to width="100%".')
    )
    latitude = forms.FloatField(
        label='Latitude', widget=forms.TextInput(attrs={}),
        required=True, help_text='* GPS Geolocation : Latitude.'
        )
    longitude = forms.FloatField(
        label='Longitude', widget=forms.TextInput(attrs={}),
        required=True, help_text='* GPS Geolocation : Longitude.'
        )
    googlemap_url = forms.CharField(
        label='Google Map URL', max_length=3000, widget=forms.TextInput(attrs={}),
        required=False, help_text=mark_safe('* Past the Google Maps Share URL. Include iframe tag.')
        )

    class Meta:
        model = Place
        fields = ("place", "images", "delete_images_flg", "themes", "delete_themes_flg", "area", "overview", "address", "tel", "url", "context", "remarks", "schedule_monthly", "schedule_weekly", "latitude", "longitude", "googlemap_url")


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
