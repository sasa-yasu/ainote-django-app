from django import forms
from django.utils import timezone
from django.utils.safestring import mark_safe
from user.models import Profile
from .models import FindMe
from .choices import GenderChoice, PrefectureChoice, HobbyChoice, FoodChoice, MusicChoice, MovieChoice, BookChoice
from .choices import PersonalityTypeChoice, FavoriteDateChoice, SenseOfValuesChoice, FuturePlanChoice, RequestForPartnerChoice
from .choices import WeekendActivityChoice, OngoingProjectChoice, SocialActivityChoice, FreeDayChoice, ProudestAchievementChoice, MostImportantValuesChoice

import logging

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

class FindMeForm(forms.ModelForm):

    name = forms.CharField(
        label='Name', max_length=100, widget=forms.TextInput(attrs={}),
        required=True, help_text='* Name should be max 100 characters.'
        )

    gender = forms.ChoiceField(
        label='Gender', choices=GenderChoice.choices(), widget=forms.RadioSelect(attrs={}),
        required=True, initial='', help_text='* Select your gender.'
    )

    images = forms.ImageField(
        label='Images', widget=forms.FileInput(attrs={}),
        required=False, help_text='* Your personal icon.'
        )
    delete_images_flg = forms.BooleanField(required=False, label='Delete Images')

    themes = forms.ImageField(
        label='Themes', widget=forms.FileInput(attrs={}),
        required=False, help_text='* Your personal theme in your profile page.'
        )
    delete_themes_flg = forms.BooleanField(required=False, label='Delete Themes')

    default_year = timezone.now().year  # 当年を基準にして選択肢を作成
    years_choice = [('', '----')] + [(year, str(year)) for year in range(default_year - 130, default_year + 1)]  # 過去130年分の年をリストとして作成
    birth_year = forms.ChoiceField(
        label='Birthday(Y)', choices=years_choice, widget=forms.Select(attrs={}),
        required=False, help_text='* If you input this, you can get the genaration-gap points.'
    )
    
    birth_month_day = forms.DateField(
        label='Birthday(M/D)', widget=forms.DateInput(attrs={'type': 'date', 'min': f'2000-01-01', 'max': f'2000-12-31'}), input_formats=['%Y-%m-%d'],
        required=False, help_text='* If you input this, you can get more accurate genaration-gap points.<br/>* bellow shows year 2000 but system ignore the year info.'
    )

    living_pref = forms.ChoiceField(
        label='Living Pref.', choices=PrefectureChoice.choices(), widget=forms.Select(attrs={}),
        required=False, help_text='* Choose a living prefecture.'
        )

    living_area = forms.CharField(
        label='Living Area', max_length=100, widget=forms.TextInput(attrs={}),
        required=False, help_text='* Living Area should be max 100 characters.'
        )

    mbti = forms.ChoiceField(
        label='MBTI Type', choices=Profile.MBTI_CHOICES, widget=forms.RadioSelect(attrs={}),
        required=False, initial='-', help_text='* Select your personal MBTI type.'
        )

    MBTI_NAME_CHOICES = Profile.MBTI_NAME_CHOICES
    mbti_name = forms.ChoiceField(
        label='MBTI Display Name', choices=[('', '---')], widget=forms.Select(attrs={}),
        required=False, initial='---', help_text='* Choose a specific name.'
        )
    
    overview = forms.CharField(
        label='Overview', max_length=100, widget=forms.TextInput(attrs={}),
        required=False, help_text='* Brief explanation. max 100 characters.'
        )

    introduce = forms.CharField(
        label='Introduce', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Detail introduction of yourself.'
        )

    hobby_choice = forms.MultipleChoiceField(
        label='Hobby Choice', choices=HobbyChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    hobby = forms.CharField(
        label='Hobby', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Hobby is...'
        )

    food_choice = forms.MultipleChoiceField(
        label='Food Choice', choices=FoodChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    food = forms.CharField(
        label='Food', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Favorite Food is...'
        )

    music_choice = forms.MultipleChoiceField(
        label='Music Choice', choices=MusicChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    music = forms.CharField(
        label='Music', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Favorite Music is...'
        )

    movie_choice = forms.MultipleChoiceField(
        label='Movie Choice', choices=MovieChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    movie = forms.CharField(
        label='Movie', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Favorite Movie is...'
        )

    book_choice = forms.MultipleChoiceField(
        label='Book Choice', choices=BookChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    book = forms.CharField(
        label='Book', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Favorite Book / Author is...'
        )

    personality_type_choice = forms.MultipleChoiceField(
        label='Personality Type Choice', choices=PersonalityTypeChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    personality_type = forms.CharField(
        label='Personality Type', widget=forms.Textarea(attrs={}),
        required=False, help_text='* My Personality Type is...'
        )

    favorite_date_choice = forms.MultipleChoiceField(
        label='Favorite Date Choice', choices=FavoriteDateChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    favorite_date = forms.CharField(
        label='Favorite Date', widget=forms.Textarea(attrs={}),
        required=False, help_text='* My Favorite Date (purpose, area etc) is...'
        )

    sense_of_values_choice = forms.MultipleChoiceField(
        label='Sense of Values Choice', choices=SenseOfValuesChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    sense_of_values = forms.CharField(
        label='Sense of Values', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Most important Sense of Value is...'
        )

    future_plan_choice = forms.MultipleChoiceField(
        label='Future Plan Choice', choices=FuturePlanChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    future_plan = forms.CharField(
        label='Future Plan', widget=forms.Textarea(attrs={}),
        required=False, help_text='* My future plan which I have / hope, is...'
        )

    request_for_partner_choice = forms.MultipleChoiceField(
        label='Request for partner Choice', choices=RequestForPartnerChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    request_for_partner = forms.CharField(
        label='Request for partner', widget=forms.Textarea(attrs={}),
        required=False, help_text='* I want this kind of status / properties / personalities for my partner.'
        )

    weekend_activity_choice = forms.MultipleChoiceField(
        label='Weekend Activity Choice', choices=WeekendActivityChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    weekend_activity = forms.CharField(
        label='Weekend Activity', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Recent Weekend Activity is...'
        )

    ongoing_project_choice = forms.MultipleChoiceField(
        label='On-Going Project Choice', choices=OngoingProjectChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    ongoing_project = forms.CharField(
        label='On-Going Project', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Current proceeding my project is...'
        )

    social_activity_choice = forms.MultipleChoiceField(
        label='Social Activity Choice', choices=SocialActivityChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    social_activity = forms.CharField(
        label='Social Activity', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Currently joined / planned event is...'
        )

    free_day_choice = forms.MultipleChoiceField(
        label='What if Free Day Choice', choices=FreeDayChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    free_day = forms.CharField(
        label='What if Free Day', widget=forms.Textarea(attrs={}),
        required=False, help_text='* If I have a Free Whole Day, What I want to do, is...'
        )

    proudest_achievements_choice = forms.MultipleChoiceField(
        label='Proudest Achieve. Choice', choices=ProudestAchievementChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    proudest_achievements = forms.CharField(
        label='Proudest Achieve.', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Proudest Achievement in my life, is...'
        )

    most_important_values_choice = forms.MultipleChoiceField(
        label='Most important Values Choice', choices=MostImportantValuesChoice.choices(), widget=forms.CheckboxSelectMultiple(attrs={}),
        required=False,
    )
    most_important_values = forms.CharField(
        label='Most important Values', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Most important Values in my life, is...'
        )

    contacts = forms.CharField(
        label='Contact', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Each contact(email, SNS account) is...'
        )

    remarks = forms.CharField(
        label='Remarks', widget=forms.Textarea(attrs={}),
        required=False, help_text='* Anything you want to share.'
        )

    class Meta:
        model = FindMe

        basic_fields        = ("name", "gender", "birth_year", "birth_month_day","living_pref","living_area")
        mbti_fields         = ("mbti", "mbti_name") 
        profile_fields      = ("overview", "introduce", "contacts", "remarks", "images", "delete_images_flg", "themes", "delete_themes_flg")
        hobbies_fields      = ("hobby_choice", "hobby", "food_choice", "food", "music_choice", "music", "movie_choice", "movie", "book_choice", "book")
        personality_fields  = ("personality_type_choice","personality_type","favorite_date_choice","favorite_date","sense_of_values_choice","sense_of_values")
        future_fields       = ("future_plan_choice","future_plan","request_for_partner_choice","request_for_partner")
        activities_fields   = ("weekend_activity_choice","weekend_activity","ongoing_project_choice","ongoing_project","social_activity_choice","social_activity")
        unique_fields       = ("free_day_choice","free_day","proudest_achievements_choice","proudest_achievements","most_important_values_choice","most_important_values")

        fields = basic_fields + mbti_fields + profile_fields + hobbies_fields + personality_fields + future_fields + activities_fields + unique_fields

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
        
        if self.instance:  # インスタンスが存在する場合（つまり、更新時）
            # birth_year に既存のデータ（インスタンスのフィールド値）を設定
            self.fields['birth_year'].initial = str(self.instance.birth_year)
            
        # birth_month_day を年を除いた月日（MM-DD）のみとして表示する
        if self.instance.birth_month_day:
            self.fields['birth_month_day'].initial = self.instance.birth_month_day.strftime('%Y-%m-%d')

        # `POST` データがあれば取得（なければ `instance.mbti` を使用）
        mbti_value = None
        if 'data' in kwargs:
            mbti_value = kwargs['data'].get('mbti')
        if not mbti_value and self.instance:
            mbti_value = self.instance.mbti
        logger.debug(f'mbti_value={mbti_value}')

        # `mbti_name` の選択肢を取得
        self.fields['mbti_name'].choices = Profile.MBTI_NAME_CHOICES.get(mbti_value, [("", "---------")])
        logger.debug(f"self.fields['mbti_name'].choices={self.fields['mbti_name'].choices}")


    def clean(self):
        cleaned_data = super().clean()

        birth_year = cleaned_data.get('birth_year')
        birth_month_day = cleaned_data.get('birth_month_day')

        if birth_month_day and not birth_year:
            self.add_error('birth_year', 'Birth year is required if you specify a date.')

        mbti  = cleaned_data.get('mbti')
        mbti_name = cleaned_data.get('mbti_name')

        if mbti_name and mbti == '-':
            self.add_error('mbti', 'MBTI is required if you specify a MBTI Name.')


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

    def clean_hobby_choice(self):
        data = self.cleaned_data.get('hobby_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_food_choice(self):
        data = self.cleaned_data.get('food_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_music_choice(self):
        data = self.cleaned_data.get('music_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_movie_choice(self):
        data = self.cleaned_data.get('movie_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_book_choice(self):
        data = self.cleaned_data.get('book_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_personality_type_choice(self):
        data = self.cleaned_data.get('personality_type_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_favorite_date_choice(self):
        data = self.cleaned_data.get('favorite_date_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_sense_of_values_choice(self):
        data = self.cleaned_data.get('sense_of_values_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_future_plan_choice(self):
        data = self.cleaned_data.get('future_plan_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_request_for_partner_choice(self):
        data = self.cleaned_data.get('request_for_partner_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_weekend_activity_choice(self):
        data = self.cleaned_data.get('weekend_activity_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_ongoing_project_choice(self):
        data = self.cleaned_data.get('ongoing_project_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_social_activity_choice(self):
        data = self.cleaned_data.get('social_activity_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_free_day_choice(self):
        data = self.cleaned_data.get('free_day_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_proudest_achievements_choice(self):
        data = self.cleaned_data.get('proudest_achievements_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data

    def clean_most_important_values_choice(self):
        data = self.cleaned_data.get('most_important_values_choice', [])
        if len(data) > 3: raise forms.ValidationError("最大3つまで選択できます。")
        return data
