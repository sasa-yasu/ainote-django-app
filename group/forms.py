from django.utils.safestring import mark_safe
from django import forms
from .models import Group

class GroupForm(forms.ModelForm):
    name = forms.CharField(
        label='Name', max_length=100, widget=forms.TextInput(attrs={}),
        required=True, help_text='* Name should be max 100 characters.'
    )
    images = forms.ImageField(
        label='Images', widget=forms.FileInput(attrs={}),
        required=False, help_text='* Image file size will be adjusted to 300px X 300px.'
    )
    delete_images_flg = forms.BooleanField(required=False, label='Delete Images')
    themes = forms.ImageField(
        label='Themes', widget=forms.FileInput(attrs={}),
        required=False, help_text='* Image file size will be adjusted to 3000px X 3000px.'
    )
    delete_themes_flg = forms.BooleanField(required=False, label='Delete Themes')
    category_choice = forms.MultipleChoiceField(
        label='Category Choice', choices=Group.CATEGORY_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class':'form-check-input'}),
        required=False,
    )
    context = forms.CharField(
        label='Context', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Shorter is better.'
    )
    remarks = forms.CharField(
        label='Remarks', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Anything you want to share.'
    )
    schedule_monthly = forms.CharField(
        label='Schedule Monthly', max_length=1028, widget=forms.TextInput(attrs={}),
        required=False, help_text=mark_safe('* Past the google schedule monthly URL (start with "&lt;iframe&gt;" tag).<br/>* Should change width-setting to width="100%".')
    )
    schedule_weekly = forms.CharField(
        label='Schedule Weekly', max_length=1028, widget=forms.TextInput(attrs={}),
        required=False, help_text=mark_safe('* Past the google schedule weekly URL (start with "&lt;iframe&gt;" tag).<br/>* Should change width-setting to width="100%".')
    )
    task_control = forms.CharField(
        label='Task Control', max_length=1028, widget=forms.TextInput(attrs={}),
        required=False, help_text=mark_safe('* Past the notion task-boad URL (start with "&lt;iframe&gt;" tag and should be end with "&lt;&#47;iframe&gt;" tag).<br/>* Should change height-setting to height="1000px".')
    )

    class Meta:
        model = Group
        fields = ("name", "images", "delete_images_flg", "themes", "delete_themes_flg", "category_choice", "context", "remarks", "schedule_monthly", "schedule_weekly", "task_control")

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

    def clean_category_choice(self):
        data = self.cleaned_data.get('category_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data
