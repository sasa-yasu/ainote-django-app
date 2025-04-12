from django import forms
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from user.models import Profile
from .models import FindMe

import logging

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

class FindMeForm(forms.ModelForm):

    name = forms.CharField(
        label='Name', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=True, help_text='* Name should be max 100 characters.'
        )

    gender = forms.ChoiceField(
        label='Gender', choices=FindMe.GENDER_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True, initial='', help_text='* Select your gender.'
    )

    images = forms.ImageField(
        label='Images', widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False, help_text='* Your personal icon.'
        )

    themes = forms.ImageField(
        label='Themes', widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False, help_text='* Your personal theme in your profile page.'
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

    living_pref = forms.ChoiceField(
        label='Living Pref.', choices=FindMe.PREFECTURE_CHOICES, widget=forms.Select(attrs={'class':'form-control'}),
        required=False, help_text='* Choose a living prefecture.'
        )

    living_area = forms.CharField(
        label='Living Area', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False, help_text='* Living Area should be max 100 characters.'
        )

    mbti = forms.ChoiceField(
        label='MBTI Type', choices=Profile.MBTI_CHOICES, widget=forms.RadioSelect(attrs={'class': 'form-check-input', 'id': 'id_mbti'}),
        required=False, initial='-', help_text='* Select your personal MBTI type.'
        )

    MBTI_NAME_CHOICES = Profile.MBTI_NAME_CHOICES
    mbti_name = forms.ChoiceField(
        label='MBTI Display Name', choices=[], widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_mbti_name'}),
        required=False, help_text='* Choose a specific name.'
        )
    
    overview = forms.CharField(
        label='Overview', max_length=100, widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False, help_text='* Brief explanation. max 100 characters.'
        )

    introduce = forms.CharField(
        label='Introduce', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Detail introduction of yourself.'
        )

    hobby_choice = forms.MultipleChoiceField(
        label='Hobby Choice', choices=FindMe.HOBBY_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    hobby = forms.CharField(
        label='Hobby', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Hobby is...'
        )

    food_choice = forms.MultipleChoiceField(
        label='Food Choice', choices=FindMe.FOOD_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    food = forms.CharField(
        label='Food', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Favorite Food is...'
        )

    music_choice = forms.MultipleChoiceField(
        label='Music Choice', choices=FindMe.MUSIC_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    music = forms.CharField(
        label='Music', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Favorite Music is...'
        )

    movie_choice = forms.MultipleChoiceField(
        label='Movie Choice', choices=FindMe.MOVIE_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    movie = forms.CharField(
        label='Movie', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Favorite Movie is...'
        )

    book_choice = forms.MultipleChoiceField(
        label='Book Choice', choices=FindMe.BOOK_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    book = forms.CharField(
        label='Book', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Favorite Book / Author is...'
        )

    personality_type_choice = forms.MultipleChoiceField(
        label='Personality Type Choice', choices=FindMe.PERSONALITY_TYPE_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    personality_type = forms.CharField(
        label='Personality Type', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* My Personality Type is...'
        )

    favorite_date_choice = forms.MultipleChoiceField(
        label='Favorite Date Choice', choices=FindMe.FAVORITE_DATE_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    favorite_date = forms.CharField(
        label='Favorite Date', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* My Favorite Date (purpose, area etc) is...'
        )

    sense_of_values_choice = forms.MultipleChoiceField(
        label='Sense of Values Choice', choices=FindMe.SENSE_OF_VALUES_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    sense_of_values = forms.CharField(
        label='Sense of Values', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Most important Sense of Value is...'
        )

    future_plan_choice = forms.MultipleChoiceField(
        label='Future Plan Choice', choices=FindMe.FUTURE_PLAN_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    future_plan = forms.CharField(
        label='Future Plan', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* My future plan which I have / hope, is...'
        )

    request_for_partner_choice = forms.MultipleChoiceField(
        label='Request for partner Choice', choices=FindMe.REQUEST_FOR_PARTNER_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    request_for_partner = forms.CharField(
        label='Request for partner', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* I want this kind of status / properties / personalities for my partner.'
        )

    weekend_activity_choice = forms.MultipleChoiceField(
        label='Weekend Activity Choice', choices=FindMe.WEEKEND_ACTIVITY_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    weekend_activity = forms.CharField(
        label='Weekend Activity', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Recent Weekend Activity is...'
        )

    ongoing_project_choice = forms.MultipleChoiceField(
        label='On-Going Project Choice', choices=FindMe.ONGOING_PROJECT_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    ongoing_project = forms.CharField(
        label='On-Going Project', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Current proceeding my project is...'
        )

    social_activity_choice = forms.MultipleChoiceField(
        label='Social Activity Choice', choices=FindMe.SOCIAL_ACTIVITY_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    social_activity = forms.CharField(
        label='Social Activity', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Currently joined / planned event is...'
        )

    free_day_choice = forms.MultipleChoiceField(
        label='What if Free Day Choice', choices=FindMe.FREE_DAY_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    free_day = forms.CharField(
        label='What if Free Day', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* If I have a Free Whole Day, What I want to do, is...'
        )

    proudest_achievements_choice = forms.MultipleChoiceField(
        label='Proudest Achieve. Choice', choices=FindMe.PROUDEST_ACHIEVEMENTS_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    proudest_achievements = forms.CharField(
        label='Proudest Achieve.', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Proudest Achievement in my life, is...'
        )

    most_important_values_choice = forms.MultipleChoiceField(
        label='Most important Values Choice', choices=FindMe.MOST_IMPORTANT_VALUES_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
    )
    most_important_values = forms.CharField(
        label='Most important Values', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Most important Values in my life, is...'
        )

    contacts = forms.CharField(
        label='Contact', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Each contact(email, SNS account) is...'
        )

    remarks = forms.CharField(
        label='Remarks', widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False, help_text='* Anything you want to share.'
        )

    class Meta:
        model = FindMe
        fields = ("name", "gender", "birth_year", "birth_month_day","living_pref","living_area",
                  "mbti", "mbti_name", 
                  "overview", "introduce", 
                  "hobby_choice", "hobby", "food_choice", "food_choice", "food", "music_choice", "music", "movie_choice", "movie", "book_choice", "book",
                  "personality_type_choice","personality_type","favorite_date_choice","favorite_date","sense_of_values_choice","sense_of_values",
                  "future_plan_choice","future_plan","request_for_partner_choice","request_for_partner",
                  "weekend_activity_choice","weekend_activity","ongoing_project_choice","ongoing_project","social_activity_choice","social_activity",
                  "free_day_choice","free_day","proudest_achievements_choice","proudest_achievements","most_important_values_choice","most_important_values",
                  "contacts", "remarks", "images", "themes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field.required:
                field.label = f"{field.label} <span style='color: red; font-size:10pt;'>(*)</span>" # if required field, show "(*)"
        
        if self.instance:  # インスタンスが存在する場合（つまり、更新時）
            # birth_year に既存のデータ（インスタンスのフィールド値）を設定
            self.fields['birth_year'].initial = str(self.instance.birth_year)
            
        # birth_month_day を年を除いた月日（MM-DD）のみとして表示する
        if self.instance.birth_month_day:
            self.fields['birth_month_day'].initial = f"{self.instance.birth_month_day}"

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

    def clean_favorite_date_choice(self):
        data = self.cleaned_data.get('favorite_date_choice', [])
        if len(data) > 3:
            raise forms.ValidationError("最大3つまで選択できます。")
        return data
    