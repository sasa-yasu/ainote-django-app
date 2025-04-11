import logging
from django.db import models
from django.utils import timezone
from user.models import Profile
from middleware.current_request import get_current_request
from AinoteProject.utils import crop_square_image, crop_16_9_image, get_mbti_compatibility, get_mbti_detail_url

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

class FindMe(models.Model):
    """Find-Me"""

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='findmes')
    name = models.CharField('Name', max_length=100, null=True, blank=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Secret'),
    ]
    gender = models.CharField('Gender', max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    images = models.ImageField('Images', upload_to='findme', null=True, blank=True)
    themes = models.ImageField('Themes', upload_to='findme', null=True, blank=True)

    default_year = timezone.now().year  # 当年を基準にして選択肢を作成
    years_choice = [(year, str(year)) for year in range(default_year - 130, default_year + 1)]  # 過去130年分の年をリストとして作成
    birth_year = models.PositiveIntegerField('Birthday(Y)', choices=years_choice, null=True, blank=True)  # 年を保存
    birth_month_day = models.DateField('Birth(M/D))', null=True, blank=True)  # 月日を保存、デフォルトは12月31日
    living_area = models.CharField('Living Area', max_length=255, null=True, blank=True)

    mbti = models.CharField('MBTI Type', max_length=4, choices=Profile.MBTI_CHOICES, null=True, blank=True)
    mbti_name = models.CharField(max_length=100, null=True, blank=True)

    overview = models.CharField('Overview', max_length=255, null=True, blank=True)
    introduce = models.TextField('Introduce', null=True, blank=True)

    hobby = models.TextField('Hobby', null=True, blank=True)
    food = models.TextField('Food', null=True, blank=True)
    music = models.TextField('Music', null=True, blank=True)
    movie = models.TextField('Movie', null=True, blank=True)
    book = models.TextField('Book', null=True, blank=True)

    favorite_type = models.TextField('Favorite Type', null=True, blank=True)
    favorite_date = models.TextField('Favorite Date', null=True, blank=True)
    sense_of_values = models.TextField('Sense of Values', null=True, blank=True)

    future_plan = models.TextField('Future Plan', null=True, blank=True)
    request_for_partner = models.TextField('Request for partner', null=True, blank=True)

    weekend_activity = models.TextField('Weekend Activity', null=True, blank=True)
    on_going_project = models.TextField('On-Going Project', null=True, blank=True)
    on_going_event = models.TextField('On-Going Event', null=True, blank=True)

    what_you_want_to_do = models.TextField('What you want to do', null=True, blank=True)
    most_proud_event = models.TextField('Most proud Event', null=True, blank=True)
    what_you_value_most = models.TextField('What you value most', null=True, blank=True)

    contacts = models.TextField('Contact', null=True, blank=True)
    remarks = models.TextField('Remarks', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='findme_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField(auto_now=True)
    updated_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='findme_updated_pics')  # 紐づくProfileが削除されたらNULL設定

    class Meta:
        pass

    def __str__(self):
        return f'<FindMe:name={self.name}, {self.profile.nick_name}>'

    def get_mbti_choices(self):
        """選択した MBTI に応じた表示名称の選択肢を返す"""
        return self.profile.MBTI_NAME_CHOICES.get(self.mbti, [])

    def get_mbti_name_display(self):
        """mbti_name のラベルを取得する"""
        for choices in self.profile.MBTI_NAME_CHOICES.values():
            for key, label in choices:
                if key == self.mbti_name:
                    return label
        return ""

    @property
    def get_mbti_url(self):
        """選択した MBTI に応じた詳細説明画面URLを返す"""
        return get_mbti_detail_url(self.mbti)

    @property
    def get_mbti_comp(self):
        request = get_current_request()  # 現在のリクエストを取得
        logger.debug(f'request={request}')
        logger.debug(f'hasattr(request, "user")={hasattr(request, "user")}')
        logger.debug(f'hasattr(request.user, "profile")={hasattr(request.user, "profile")}')
        if request and hasattr(request, 'user') and hasattr(request.user, 'profile'):
            user_profile = request.user.profile
            logger.debug(f'user_profile.mbti={user_profile.mbti}')
            logger.debug(f'self.mbti={self.mbti}')
            if user_profile.mbti and self.mbti:
                logger.debug(f'get_mbti_compatibility')
                return get_mbti_compatibility(user_profile.mbti, self.mbti)
        return None, None
    
    def save(self, *args, **kwargs):
        if self.images and self.images != self.__class__.objects.get(pk=self.pk).images: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            self.images = crop_square_image(self.images, 300) # Update the images size

        if self.themes and self.themes != self.__class__.objects.get(pk=self.pk).themes: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            self.themes = crop_16_9_image(self.themes, 1500) # Update the themes size

        """mbti_name が現在の mbti に対応しているかチェック"""
        if self.mbti and self.mbti_name:
            valid_choices = dict(self.profile.MBTI_NAME_CHOICES.get(self.mbti, []))
            if self.mbti_name not in valid_choices:
                self.mbti_name = None  # 無効な場合はクリア

        super().save(*args, **kwargs)


class FindMeImage(models.Model):
    """FindMe に紐づく画像（複数可）"""
    findme = models.ForeignKey('FindMe', on_delete=models.CASCADE, related_name='findme_images')
    image = models.ImageField(upload_to='findme/images')
    caption = models.CharField(max_length=255, blank=True, null=True)  # 任意のキャプション

    is_theme = models.BooleanField(default=False)  # テーマ画像フラグ（Trueならテーマ画像として扱う）

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.findme.name or "Unknown"} (Theme: {self.is_theme})'
