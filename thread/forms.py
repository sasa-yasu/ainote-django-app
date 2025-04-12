from django import forms
from chat.forms import ChatForm
from .models import Thread, ThreadChat

class ThreadForm(forms.ModelForm):

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
        required=False, help_text='* Image file size will be adjusted to 1500px X 1500px.'
    )
    category_choice = forms.MultipleChoiceField(
        label='Category Choice', choices=Thread.CATEGORY_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
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
        model = Thread
        fields = ("name", "images", "themes", "category_choice", "overview", "context", "remarks")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} <span style='color: red; font-size:10pt;'>(*)</span>" # if required field, show "(*)"


class ThreadChatForm(ChatForm):

    # overwrite
    class Meta:
        model = ThreadChat
        fields = ("title", "context", "images", "author")
