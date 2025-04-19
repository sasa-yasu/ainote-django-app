from django import forms
from .models import Chat

class ChatForm(forms.ModelForm):
    """問い合わせ用フォーム"""
    title = forms.CharField(
        label='Title', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=True, help_text='* Title should be max 100 characters.'
    )
    context = forms.CharField(
        label='Context', widget=forms.Textarea(attrs={'class':'form-control'}),
        required=False, help_text='* Shorter is better.'
    )
    images = forms.ImageField(
        label='Images', widget=forms.FileInput(attrs={'class':'form-control'}),
        required=False, help_text='* Image file size will be adjusted to 300px X 300px.'
    )
    delete_images_flg = forms.BooleanField(required=False, label='Delete Images')
    author = forms.CharField(
        label='Author', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=True, help_text='* Can input anything for superuser.'
    )

    class Meta:
        model = Chat
        fields = ("title", "context", "images", "delete_images_flg", "author")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} <span style='color: red; font-size:10pt;'>(*)</span>" # if required field, show "(*)"
