from django.utils.safestring import mark_safe
from django import forms
from .models import SharedFile

class SharedFileForm(forms.ModelForm):

    title = forms.CharField(
        label='Title', max_length=100, widget=forms.TextInput(attrs={}),
        required=True, help_text='* Title should be max 100 characters.'
    )
    images = forms.ImageField(
        label='Images', widget=forms.FileInput(attrs={}),
        required=False, help_text='* Image file size will be adjusted to 300px X 300px.'
    )
    delete_images_flg = forms.BooleanField(required=False, label='Delete Images')
    themes = forms.ImageField(
        label='Themes', widget=forms.FileInput(attrs={}),
        required=False, help_text='* Image file size will be adjusted to 1500px X 1500px.'
    )
    delete_themes_flg = forms.BooleanField(required=False, label='Delete Themes')
    category_choice = forms.MultipleChoiceField(
        label='Category Choice', choices=SharedFile.CATEGORY_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    files = forms.FileField(
        label='Files', widget=forms.FileInput(attrs={}),
        required=False, help_text='* Uploaded file size is up-to 50M.'
    )
    overview = forms.CharField(
        label='Overview', max_length=100, widget=forms.TextInput(attrs={}),
        required=False, help_text='* What kind of topic, you wan to share / get.'
    )
    context = forms.CharField(
        label='Context', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Shorter is better.'
    )
    remarks = forms.CharField(
        label='Remarks', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Anything you want to share.'
    )

    class Meta:
        model = SharedFile
        fields = ("title", "images", "delete_images_flg", "themes", "delete_themes_flg", "category_choice", "files", "overview", "context", "remarks")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.TextInput, forms.Select, forms.Textarea, forms.DateInput)):
                widget.attrs.setdefault('class', 'form-control')
            if isinstance(widget, (forms.RadioSelect, forms.CheckboxSelectMultiple)):
                widget.attrs.setdefault('class', 'form-check-input')

            if field.required:
                field.label = mark_safe(f"{field.label} <span style='color: red; font-size:10pt;'>(*)</span>") # if required field, show "(*)"

    def clean_category_choice(self):
        data = self.cleaned_data.get('category_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data
