from django import forms
from .models import SharedFile

class SharedFileForm(forms.ModelForm):

    title = forms.CharField(
        label='Title', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=True, help_text='* Title should be max 100 characters.'
    )
    images = forms.ImageField(
        label='Images', widget=forms.FileInput(attrs={'class':'form-control'}),
        required=False, help_text='* Image file size will be adjusted to 300px X 300px.'
    )
    themes = forms.ImageField(
        label='Themes', widget=forms.FileInput(attrs={'class':'form-control'}),
        required=False, help_text='* Image file size will be adjusted to 1500px X 1500px.'
    )
    category_choice = forms.MultipleChoiceField(
        label='Category Choice', choices=SharedFile.CATEGORY_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    files = forms.FileField(
        label='Files', widget=forms.FileInput(attrs={'class':'form-control'}),
        required=False, help_text='* Uploaded file size is up-to 50M.'
    )
    overview = forms.CharField(
        label='Overview', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False, help_text='* What kind of topic, you wan to share / get.'
    )
    context = forms.CharField(
        label='Context', widget=forms.Textarea(attrs={'class':'form-control'}),
        required=False, help_text='* Shorter is better.'
    )
    remarks = forms.CharField(
        label='Remarks', widget=forms.Textarea(attrs={'class':'form-control'}),
        required=False, help_text='* Anything you want to share.'
    )

    class Meta:
        model = SharedFile
        fields = ("title", "images", "themes", "category_choice", "files", "overview", "context", "remarks")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} <span style='color: red; font-size:10pt;'>(*)</span>" # if required field, show "(*)"
