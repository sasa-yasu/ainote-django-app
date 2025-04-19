import logging
from django.db import models
from django.utils import timezone
from multiselectfield import MultiSelectField
from django.db.models import Q
from user.models import Profile
from middleware.current_request import get_current_request
from AinoteProject.utils import crop_square_image, crop_16_9_image, get_mbti_compatibility, get_mbti_detail_url
from .choices import GenderChoice, PrefectureChoice, HobbyChoice, FoodChoice, MusicChoice, MovieChoice, BookChoice
from .choices import PersonalityTypeChoice, FavoriteDateChoice, SenseOfValuesChoice, FuturePlanChoice, RequestForPartnerChoice
from .choices import WeekendActivityChoice, OngoingProjectChoice, SocialActivityChoice, FreeDayChoice, ProudestAchievementChoice, MostImportantValuesChoice

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

class FindMe(models.Model):
    """Find-Me"""

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='findmes')

    ##### 基本情報 #####
    # 名前
    name = models.CharField('Name', max_length=100, null=True, blank=True)
    # 性別
    gender = models.CharField('Gender', max_length=1, choices=GenderChoice.choices(), null=True, blank=True)
    # アイコン画像＆背景画像
    images = models.ImageField('Images', upload_to='findme', null=True, blank=True)
    themes = models.ImageField('Themes', upload_to='findme', null=True, blank=True)
    #  生年月日
    default_year = timezone.now().year  # 当年を基準にして選択肢を作成
    years_choice = [(year, str(year)) for year in range(default_year - 130, default_year + 1)]  # 過去130年分の年をリストとして作成
    birth_year = models.PositiveIntegerField('Birthday(Y)', choices=years_choice, null=True, blank=True)  # 年を保存
    birth_month_day = models.DateField('Birth(M/D))', null=True, blank=True)  # 月日を保存、デフォルトは12月31日

    # 居住地(都道府県)
    living_pref = models.CharField('Living Pref.', max_length=10, choices=PrefectureChoice.choices(), null=True, blank=True)
    # 居住地
    living_area = models.CharField('Living Area', max_length=255, null=True, blank=True)
    # MBTI
    mbti = models.CharField('MBTI Type', max_length=4, choices=Profile.MBTI_CHOICES, null=True, blank=True)
    mbti_name = models.CharField(max_length=100, null=True, blank=True)

    ##### 自己紹介 #####
    # 短い自己紹介文
    overview = models.CharField('Overview', max_length=255, null=True, blank=True)
    # 長文の自己紹介
    introduce = models.TextField('Introduce', null=True, blank=True)

    ##### 趣味・興味 #####
    # 趣味（例：映画鑑賞、読書、旅行、スポーツ、音楽など） 
    hobby_choice = MultiSelectField('Hobby Choice', max_length=200, choices=HobbyChoice.choices(), null=True, blank=True)
    hobby = models.TextField('Hobby', null=True, blank=True)
    # 好きな食べ物：共通の好みがあれば話題作りに使えます。
    food_choice = MultiSelectField('Food Choice', max_length=200, choices=FoodChoice.choices(), null=True, blank=True)
    food = models.TextField('Food', null=True, blank=True)
    # 好きな音楽：自分の好みを伝えることで、相性の良い相手を見つけやすくなります。
    music_choice = MultiSelectField('Music Choice', max_length=200, choices=MusicChoice.choices(), null=True, blank=True)
    music = models.TextField('Music', null=True, blank=True)
    # 好きな映画：自分の好みを伝えることで、相性の良い相手を見つけやすくなります。
    movie_choice = MultiSelectField('Movie Choice', max_length=200, choices=MovieChoice.choices(), null=True, blank=True)
    movie = models.TextField('Movie', null=True, blank=True)
    # 好きな本：自分の好みを伝えることで、相性の良い相手を見つけやすくなります。
    book_choice = MultiSelectField('Book Choice', max_length=200, choices=BookChoice.choices(), null=True, blank=True)
    book = models.TextField('Book', null=True, blank=True)

    ##### 性格や価値観 #####
    # 自分の性格タイプ（例：おおらか、真面目、社交的、落ち着いている、マイペースなど）
    personality_type_choice = MultiSelectField('Favorite Type Choice', max_length=200, choices=PersonalityTypeChoice.choices(), null=True, blank=True)
    personality_type = models.TextField('Favorite Type', null=True, blank=True)
    # 理想のデート：どんなデートが好きか、またはどんな相手と一緒に楽しみたいかを記載。
    favorite_date_choice = MultiSelectField('Favorite Date Choice', max_length=200, choices=FavoriteDateChoice.choices(), null=True, blank=True)
    favorite_date = models.TextField('Favorite Date', null=True, blank=True)
    # 重視する価値観（例：誠実、家族重視、成長志向、自由を大切にするなど）
    sense_of_values_choice = MultiSelectField('Sense of Values Choice', max_length=200, choices=SenseOfValuesChoice.choices(), null=True, blank=True)
    sense_of_values = models.TextField('Sense of Values', null=True, blank=True)

    ##### 目標・将来のビジョン #####
    # 今後のキャリアや人生でやりたいこと：将来のビジョンや計画について簡単に触れる。
    future_plan_choice = MultiSelectField('Future Plan Choice', max_length=200, choices=FuturePlanChoice.choices(), null=True, blank=True)
    future_plan = models.TextField('Future Plan', null=True, blank=True)
    # 理想のパートナー像：どんな性格や価値観のパートナーを求めているかを伝える。
    request_for_partner_choice = MultiSelectField('Request for partner Choice', max_length=200, choices=RequestForPartnerChoice.choices(), null=True, blank=True)
    request_for_partner = models.TextField('Request for partner', null=True, blank=True)

    ##### 興味のある活動 #####
    # 週末の過ごし方：どのように週末を過ごすのが好きか（例：アウトドア、映画、カフェ巡りなど）。
    weekend_activity_choice = MultiSelectField('Weekend Activity Choice', max_length=200, choices=WeekendActivityChoice.choices(), null=True, blank=True)
    weekend_activity = models.TextField('Weekend Activity', null=True, blank=True)
    # 今やっている活動／プロジェクト：仕事やプライベートで挑戦していること、趣味でやっていること。
    ongoing_project_choice = MultiSelectField('On-Going Project Choice', max_length=200, choices=OngoingProjectChoice.choices(), null=True, blank=True)
    ongoing_project = models.TextField('On-Going Project', null=True, blank=True)

    ##### 社会的な活動・ボランティア #####
    # 参加している社会活動やボランティア：自分の社会貢献やコミュニティ活動を記載（相手に共感を呼びやすい）。
    social_activity_choice = MultiSelectField('Social Activity Choice', max_length=200, choices=SocialActivityChoice.choices(), null=True, blank=True)
    social_activity = models.TextField('Social Activity', null=True, blank=True)

    ##### ユニークな質問 #####
    # もしも自由に過ごせる1日があったら何をしたいか？
    free_day_choice = MultiSelectField('Free Day Choice', max_length=200, choices=FreeDayChoice.choices(), null=True, blank=True)
    free_day = models.TextField('What if Free Day', null=True, blank=True)
    # 今までの人生で最も誇りに思うことは何か？
    proudest_achievements_choice = MultiSelectField('Proudest Achievement Choice', max_length=200, choices=ProudestAchievementChoice.choices(), null=True, blank=True)
    proudest_achievements = models.TextField('Proudest Achieve.', null=True, blank=True)
    # 最も大切にしていることは？
    most_important_values_choice = MultiSelectField('Most important Values Choice', max_length=200, choices=MostImportantValuesChoice.choices(), null=True, blank=True)
    most_important_values = models.TextField('Most important Values', null=True, blank=True)

    contacts = models.TextField('Contact', null=True, blank=True)
    remarks = models.TextField('Remarks', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='findme_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField(auto_now=True)
    updated_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='findme_updated_pics')  # 紐づくProfileが削除されたらNULL設定

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
    
    @classmethod
    def get_all_choices(cls, context):
        context.update({'GENDER_CHOICES': GenderChoice.choices()})
        context.update({'HOBBY_CHOICES': HobbyChoice.choices()})
        context.update({'FOOD_CHOICES': FoodChoice.choices()})
        context.update({'MUSIC_CHOICES': MusicChoice.choices()})
        context.update({'MOVIE_CHOICES': MovieChoice.choices()})
        context.update({'BOOK_CHOICES': BookChoice.choices()})
        context.update({'PERSONALITY_TYPE_CHOICES': PersonalityTypeChoice.choices()})
        context.update({'FAVORITE_DATE_CHOICES': FavoriteDateChoice.choices()})
        context.update({'SENSE_OF_VALUES_CHOICES': SenseOfValuesChoice.choices()})
        context.update({'FUTURE_PLAN_CHOICES': FuturePlanChoice.choices()})
        context.update({'REQUEST_FOR_PARTNER_CHOICES': RequestForPartnerChoice.choices()})
        context.update({'WEEKEND_ACTIVITY_CHOICES': WeekendActivityChoice.choices()})
        context.update({'ONGOING_PROJECT_CHOICES': OngoingProjectChoice.choices()})
        context.update({'SOCIAL_ACTIVITY_CHOICES': SocialActivityChoice.choices()})
        context.update({'FREE_DAY_CHOICES': FreeDayChoice.choices()})
        context.update({'PROUDEST_ACHIEVEMENTS_CHOICES': ProudestAchievementChoice.choices()})
        context.update({'MOST_IMPORTANT_VALUES_CHOICES': MostImportantValuesChoice.choices()})

        return context
    
    @classmethod
    def filter_findme_object(cls, object_list, object_field, field_name, choices):
        
        if not object_field: return object_list
        # 選択肢のバリデーション
        valid_choices = [choice[0] for choice in choices]
        logger.debug(f'valid_choices: {valid_choices}')

        object = [choice for choice in object_field if choice in valid_choices]
        logger.debug(f'object: {object}')
        # フィルタ処理
        if object:
            q = Q()
            for choice in object:
                logger.debug(f'field_name: {field_name} include choice={choice}')
                q |= Q(**{f"{field_name}__icontains": choice})
            logger.debug(f'object_list: {object_list}')
            object_list = object_list.filter(q)
        return object_list

    def save(self, *args, **kwargs):
        if self.pk:
            orig = self.__class__.objects.filter(pk=self.pk).first()
            if self.images and orig and self.images != orig.images: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
                self.images = crop_square_image(self.images, 300) # Update the images size

            if self.themes and orig and self.themes != orig.themes: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
                self.themes = crop_16_9_image(self.themes, 1500) # Update the themes size

        """mbti_name が現在の mbti に対応しているかチェック"""
        if self.mbti and self.mbti_name:
            valid_choices = dict(self.profile.MBTI_NAME_CHOICES.get(self.mbti, []))
            if self.mbti_name not in valid_choices:
                self.mbti_name = None  # 無効な場合はクリア

        super().save(*args, **kwargs)

    # 受け取った Poke数 を表示
    @property
    def poke_count(self):
        return self.received_pokes.count()
    
    @property
    def get_all_notifications(self):
        """ すべての通知を取得 """
        return self.recipient_notifications.all().order_by("-created_at")

class FindMeImage(models.Model):
    """FindMe に紐づく画像（複数可）"""
    findme = models.ForeignKey('FindMe', on_delete=models.CASCADE, related_name='findme_images')
    IMAGE_CATEGORY_CHOICES = [
        ('smile', '😊笑顔😄'),
        ('fashion', '👗オシャレ🕶️'),
        ('hobby_action', '🎨趣味🎸'),
        ('pet_love', '🐶ペット🐱'),
        ('outdoor', '🌄自然・お出かけ🚴'),
        ('sports_pose', '🏋️‍♂️スポーツ・健康美💪'),
        ('foodie', '🍳手料理・グルメ🍰'),
        ('culture', '📚知的・文化的🧠'),
        ('mystery', '🎭ミステリアス🌙'),
        ('funny', '😂ユーモア🤪'),
    ]
    image_category_choice = models.CharField('Image Category', max_length=100, choices=IMAGE_CATEGORY_CHOICES, null=True, blank=True)
    image = models.ImageField(upload_to='findme/images')
    caption = models.CharField(max_length=255, blank=True, null=True)  # 任意のキャプション

    is_theme = models.BooleanField(default=False)  # テーマ画像フラグ（Trueならテーマ画像として扱う）

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.findme.name or "Unknown"} (Theme: {self.is_theme})'


class Poke(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_pokes')
    receiver = models.ForeignKey(FindMe, on_delete=models.CASCADE, related_name='received_pokes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} poked {self.receiver} on {self.created_at}'

class Notification(models.Model):
    recipient = models.ForeignKey(FindMe, on_delete=models.CASCADE, related_name='recipient_notifications')
    sender = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='sender_notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
