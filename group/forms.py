from django import forms
from .models import Group

class GroupForm(forms.ModelForm):
    name = forms.CharField(
        label='Name', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=True, help_text='* Name should be max 100 characters.'
    )
    images = forms.ImageField(
        label='Images', widget=forms.FileInput(attrs={'class':'form-control'}),
        required=False, help_text='* Image file size will be adjusted to 300px X 300px.'
    )
    themes = forms.ImageField(
        label='Themes', widget=forms.FileInput(attrs={'class':'form-control'}),
        required=False, help_text='* Image file size will be adjusted to 3000px X 3000px.'
    )
    context = forms.CharField(
        label='Context', widget=forms.Textarea(attrs={'class':'form-control'}),
        required=False, help_text='* Shorter is better.'
    )
    remarks = forms.CharField(
        label='Remarks', widget=forms.Textarea(attrs={'class':'form-control'}),
        required=False, help_text='* Anything you want to share.'
    )
    schedule_monthly = forms.CharField(
        label='Schedule Monthly', max_length=1028, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False, help_text='* Past the google schedule monthly URL (start with "iframe" tag).<br/>* Should change width-setting to width="100%".'
    )
    schedule_weekly = forms.CharField(
        label='Schedule Weekly', max_length=1028, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False, help_text='* Past the google schedule weekly URL (start with "iframe" tag).<br/>* Should change width-setting to width="100%".'
    )

    class Meta:
        model = Group
        fields = ("name", "images", "themes", "context", "remarks", "schedule_monthly", "schedule_weekly")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} <span style='color: red; font-size:10pt;'>(*)</span>" # if required field, show "(*)"
