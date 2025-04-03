from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

import logging

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

class UserCreateForm(UserCreationForm):
    username = forms.CharField(
        label='User Name', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=True, help_text='* User Name should be max 100 characters.'
        )
    
    password2 = forms.CharField(
        label='Password', max_length=100, widget=forms.PasswordInput(attrs={'class':'form-control'}),
        required=True, help_text='* Password should not be simple.'
        )

    password1 = forms.CharField(
        label='Password(again)', max_length=100, widget=forms.PasswordInput(attrs={'class':'form-control'}),
        required=True, help_text='* This should be same as above Password.'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} <span style='color: red; font-size:10pt;'>(*)</span>" # if required field, show "(*)"

class ProfileForm(forms.ModelForm):

    memberid = forms.CharField(
        label='Member ID', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=True, help_text='* MemberId should be max 100 characters.'
        )

    nick_name = forms.CharField(
        label='Nick Name', max_length=10, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=True, help_text='* Nick Name should be max 10 characters.'
        )

    BADGES_CHOICES = Profile.BADGES_CHOICES
    badges = forms.ChoiceField(
        label='Badges', choices=BADGES_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True, initial='light', help_text='* Select your personal color.'
    )
    
    birthday = forms.DateField(
        label='Birthday', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), input_formats=['%Y-%m-%d'],
        required=False, help_text='* If you share it, it might be something. You can set 9999 for YEAR. YEAR will be ignored.'
        )

    MBTI_CHOICES = Profile.MBTI_CHOICES
    mbti = forms.ChoiceField(
        label='MBTI Type', choices=MBTI_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-check-input', 'id': 'id_mbti'}),
        required=False, initial='-', help_text='* Select your personal MBTI type.'
        )

    MBTI_NAME_CHOICES = Profile.MBTI_NAME_CHOICES
    mbti_name = forms.ChoiceField(
        label='MBTI Display Name', choices=[], widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_mbti_name'}),
        required=False, help_text='* Choose a specific name.'
        )
    
    hobby = forms.CharField(
        label='Hobby', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Hobby is...'
        )

    sports = forms.CharField(
        label='Sports', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Playing / Watching Sports is...'
        )

    movie = forms.CharField(
        label='Movie', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Favorite Movie is...'
        )

    music = forms.CharField(
        label='Music', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Favorite Music is...'
        )

    book = forms.CharField(
        label='Book', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Favorite Book / Author is...'
        )

    event = forms.CharField(
        label='Event', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Joinning Event is...'
        )

    remarks = forms.CharField(
        label='Remarks', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Anything you want to share.'
        )

    images = forms.ImageField(
        label='Images', widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False, help_text='* Your personal icon.'
        )

    themes = forms.ImageField(
        label='Themes', widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False, help_text='* Your personal theme in your profile page.'
        )

    class Meta:
        model = Profile
        fields = ("memberid", "nick_name", "badges", "birthday", "mbti", "mbti_name", "hobby", "sports", "movie", "music", "book", "event", "remarks", "images", "themes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} <span style='color: red; font-size:10pt;'>(*)</span>" # if required field, show "(*)"
        
        # `POST` データがあれば取得（なければ `instance.mbti` を使用）
        if 'data' in kwargs:
            mbti_value = kwargs['data'].get('mbti', self.instance.mbti if self.instance else None)
        else:
            mbti_value = self.instance.mbti if self.instance else None

        logger.debug(f'mbti_value={mbti_value}')

        # `mbti_name` の選択肢を取得
        self.fields['mbti_name'].choices = Profile.MBTI_NAME_CHOICES.get(mbti_value, [("", "---------")])
        logger.debug(f"self.fields['mbti_name'].choices={self.fields['mbti_name'].choices}")


    def clean_mbti_name(self):
        """mbti_name が現在の mbti の選択肢に含まれているかチェック"""
        mbti_value = self.cleaned_data.get('mbti')
        mbti_name_value = self.cleaned_data.get('mbti_name')

        # `mbti_name` の選択肢をリストで取得（タプルのリストを展開）
        valid_choices = [choice[0] for choice in Profile.MBTI_NAME_CHOICES.get(mbti_value, [])]

        logger.debug(f'mbti_name_value={mbti_name_value}')
        logger.debug(f'valid_choices={valid_choices}')

        if mbti_name_value and mbti_name_value not in valid_choices:
            raise forms.ValidationError(f"MBTI Typeから再度選択してください。{mbti_name_value} は候補にありません。")

        return mbti_name_value
