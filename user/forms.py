from django import forms
from django.utils import timezone
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

    badges = forms.ChoiceField(
        label='Badges', choices=Profile.BADGES_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True, initial='light', help_text='* Select your personal color.'
    )
    
    default_year = timezone.now().year  # 当年を基準にして選択肢を作成
    years_choice = [('', '----')] + [(year, str(year)) for year in range(default_year - 130, default_year + 1)]  # 過去130年分の年をリストとして作成
    birth_year = forms.ChoiceField(
        label='Birthday(Y)', choices=years_choice, widget=forms.Select(attrs={'class': 'form-control'}),
        required=False, help_text='* If you input this, you can get the genaration-gap points.'
    )
    
    birth_month_day = forms.DateField(
        label='Birthday(M/D)', widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'min': f'2000-01-01', 'max': f'2000-12-31'}), input_formats=['%Y-%m-%d'],
        required=False, help_text='* If you input this, you can get more accurate genaration-gap points.<br/>* bellow shows year 2000 but system ignore the year info.'
    )

    mbti = forms.ChoiceField(
        label='MBTI Type', choices=Profile.MBTI_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}),
        required=False, initial='-', help_text='* Select your personal MBTI type.'
        )

    mbti_name = forms.ChoiceField(
        label='MBTI Display Name', choices=[], widget=forms.Select(attrs={'class': 'form-control'}),
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

    contract_course = forms.ChoiceField(
        label='Contract Course', choices=Profile.CONTRACT_COURSE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}),
        required=False, initial='-', help_text='* Select your contract course.'
        )
    caretaker01 = forms.CharField(
        label='Caretaker01 email', max_length=255, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False, help_text='* If input the email-address, can receive the check-in / check-out email.'
        )
    caretaker02 = forms.CharField(
        label='Caretaker02 email', max_length=255, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False, help_text='* If input the email-address, can receive the check-in / check-out email.'
        )
    caretaker03 = forms.CharField(
        label='Caretaker03 email', max_length=255, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False, help_text='* If input the email-address, can receive the check-in / check-out email.'
        )
    caretaker04 = forms.CharField(
        label='Caretaker04 email', max_length=255, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False, help_text='* If input the email-address, can receive the check-in / check-out email.'
        )
    caretaker05 = forms.CharField(
        label='Caretaker05 email', max_length=255, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False, help_text='* If input the email-address, can receive the check-in / check-out email.'
        )

    class Meta:
        model = Profile
        fields = ("memberid", "nick_name", "badges", "birth_year", "birth_month_day",
                  "mbti", "mbti_name", "hobby", "sports", "movie", "music", "book", "event", "remarks", "images", "themes",
                  "contract_course", "caretaker01", "caretaker02", "caretaker03", "caretaker04", "caretaker05")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} <span style='color: red; font-size:10pt;'>(*)</span>" # if required field, show "(*)"
        
#        if self.instance:  # インスタンスが存在する場合（つまり、更新時）
#            # birth_year に既存のデータ（インスタンスのフィールド値）を設定
#            self.fields['birth_year'].initial = str(self.instance.birth_year)
            
#        # birth_month_day を年を除いた月日（MM-DD）のみとして表示する
#        if self.instance.birth_month_day:
#            self.fields['birth_month_day'].initial = f"{self.instance.birth_month_day}"

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
