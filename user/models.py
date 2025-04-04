import logging
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models import Q
from django.db import models
from django.dispatch import receiver
from datetime import date
from django.utils import timezone
from datetime import timedelta
from middleware.current_request import get_current_request
from AinoteProject.utils import crop_square_image, crop_16_9_image, get_mbti_compatibility, get_mbti_detail_url

# ロガー取得
logger = logging.getLogger('app')
error_logger = logging.getLogger('error')

class Profile(models.Model):
    """Profile"""

    user1 = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    memberid = models.CharField('Member Id', max_length=255, null=True, blank=True)
    nick_name = models.CharField('Nick Name', max_length=255, null=True, blank=True)
    BADGES_CHOICES = [
        ('light', 'White'),
        ('primary', 'Blue'),
        ('danger', 'Red'),
        ('success', 'Green'),
        ('warning', 'Yellow'),
        ('info', 'Sky'),
        ('secondary', 'Gray'),
        ('dark', 'Black')
    ]
    badges = models.CharField('Badges', max_length=30, choices=BADGES_CHOICES, null=True, blank=True)
    birthday = models.DateField('Birthday', null=True, blank=True)

    MBTI_CHOICES = [
        ('-', '-'),
        ('INTJ', 'INTJ:想像力が豊かで、戦略的な思考の持ち主。あらゆる物事に対して計画を立てる。'),
        ('INTP', 'INTP:貪欲な知識欲を持つ革新的な発明家'),
        ('ENTJ', 'ENTJ:大胆で想像力豊か、かつ強い意志を持つ指導者。常に道を見つけるか、道を切り開く。'),
        ('ENTP', 'ENTP:賢くて好奇心旺盛な思考家。知的挑戦には必ず受けて立つ。'),
        ('INFJ', 'INFJ:物静かで神秘的だが、人々を非常に勇気づける飽くなき理想主義者'),
        ('ENFJ', 'ENFJ:カリスマ性があり、人々を励ますリーダー。聞く人を魅了する。'),
        ('INFP', 'INFP:詩人肌で親切な利他主義者。良い物事のためなら、いつでも懸命に手を差し伸べる。'),
        ('ENFP', 'ENFP:情熱的で独創力があり、かつ社交的な自由人。常に笑いほほ笑みの種を見つけられる。'),
        ('ISTJ', 'ISTJ:実用的で事実に基づいた思考の持ち主。その信頼性は紛れもなく本物。'),
        ('ISFJ', 'ISFJ:非常に献身的で心の温かい擁護者。いつでも大切な人を守る準備ができている。'),
        ('ESTJ', 'ESTJ:優秀な管理者で、物事や人々を管理する能力にかけては、右に出る者はいない。'),
        ('ESFJ', 'ESFJ:非常に思いやりがあり社交的で、人気がある。常に熱心に人々に手を差し伸べている。'),
        ('ESTP', 'ESTP:賢くてエネルギッシュで、非常に鋭い知覚の持ち主。危険と隣り合わせの人生を心から楽しむ。'),
        ('ISTP', 'ISTP:大胆で実践的な思考を持つ実験者。あらゆる道具を使いこなす。'),
        ('ISFP', 'ISFP:柔軟性と魅力がある芸術家。常に進んで物事を探索し経験しようとする。'),
        ('ESFP', 'ESFP:自発性がありエネルギッシュで熱心なエンターテイナー。周りが退屈することは決してない。'),
    ]
    mbti = models.CharField('MBTI Type', max_length=4, choices=MBTI_CHOICES, null=True, blank=True)

    MBTI_NAME_CHOICES = {
        'INTJ': [('INTJ-0','INTJ-0:建築家'),           ('INTJ-1','INTJ-1:冷静な戦略家'),          ('INTJ-2','INTJ-2:賢いフクロウ')],
        'INTP': [('INTP-0','INTP-0:論理学者'),         ('INTP-1','INTP-1:ひらめき科学者'),        ('INTP-2','INTP-2:ひらめきネコ')],
        'ENTJ': [('ENTJ-0','ENTJ-0:指揮官'),           ('ENTJ-1','ENTJ-1:カリスマ社長'),          ('ENTJ-2','ENTJ-2:リーダーライオン')],
        'ENTP': [('ENTP-0','ENTP-0:討論者'),           ('ENTP-1','ENTP-1:機転の利く弁護士'),      ('ENTP-2','ENTP-2:おしゃべりオウム')],
        'INFJ': [('INFJ-0','INFJ-0:提唱者'),           ('INFJ-1','INFJ-1:理想を追う作家'),        ('INFJ-2','INFJ-2:ひそかなユニコーン')],
        'ENFJ': [('ENFJ-0','ENFJ-0:主人公'),           ('ENFJ-1','ENFJ-1:みんなの先生'),          ('ENFJ-2','ENFJ-2:みんなのコアラ')],
        'INFP': [('INFP-0','INFP-0:仲介者'),           ('INFP-1','INFP-1:夢見る詩人'),            ('INFP-2','INFP-2:夢見るイルカ')],
        'ENFP': [('ENFP-0','ENFP-0:運動家'),           ('ENFP-1','ENFP-1:自由なクリエイター'),     ('ENFP-2','ENFP-2:わくわくリス')],
        'ISTJ': [('ISTJ-0','ISTJ-0:管理者'),           ('ISTJ-1','ISTJ-1:堅実な公務員'),          ('ISTJ-2','ISTJ-2:まじめなカメ')],
        'ISFJ': [('ISFJ-0','ISFJ-0:擁護者'),           ('ISFJ-1','ISFJ-1:優しい看護師'),          ('ISFJ-2','ISFJ-2:やさしいウサギ')],
        'ESTJ': [('ESTJ-0','ESTJ-0:幹部'),             ('ESTJ-1','ESTJ-1:頼れるリーダー'),        ('ESTJ-2','ESTJ-2:しっかりイヌ')],
        'ESFJ': [('ESFJ-0','ESFJ-0:領事'),             ('ESFJ-1','ESFJ-1:世話好きカウンセラー'),  ('ESFJ-2','ESFJ-2:お世話好きカンガルー')],
        'ESTP': [('ESTP-0','ESTP-0:起業家'),           ('ESTP-1','ESTP-1:行動派アスリート'),      ('ESTP-2','ESTP-2:チャレンジザル')],
        'ISTP': [('ISTP-0','ISTP-0:巨匠'),             ('ISTP-1','ISTP-1:職人肌のエンジニア'),    ('ISTP-2','ISTP-2:クールなワシ')],
        'ISFP': [('ISFP-0','ISFP-0:冒険家'),           ('ISFP-1','ISFP-1:アートなデザイナー'),    ('ISFP-2','ISFP-2:アートなネコ')],
        'ESFP': [('ESFP-0','ESFP-0:エンターテイナー'),  ('ESFP-1','ESFP-1:ムードメーカー俳優'),    ('ESFP-2','ESFP-2:パーティーペンギン')],
    }
    mbti_name = models.CharField(max_length=100, null=True, blank=True)

    hobby = models.TextField('Hobby', null=True, blank=True)
    sports = models.TextField('Sports', null=True, blank=True)
    movie = models.TextField('Movie', null=True, blank=True)
    music = models.TextField('Music', null=True, blank=True)
    book = models.TextField('Book', null=True, blank=True)
    event = models.TextField('Remarks', null=True, blank=True)
    remarks = models.TextField('Remarks', null=True, blank=True)
    given_likes = models.IntegerField(null=True, blank=True, default=0)

    images = models.ImageField('Images', upload_to='user', null=True, blank=True)
    themes = models.ImageField('Themes', upload_to='user', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_pic = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField(auto_now=True)
    updated_pic = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_updated_pics')  # 紐づくProfileが削除されたらNULL設定

    """ グループモデル """
    groups = models.ManyToManyField('group.Group', blank=True, related_name='profiles')  # 紐づくProfileが削除されてもChatは残る

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id'], name='profile_pk'),
        ]

    def __str__(self):
        return f'<User:id={self.memberid}, {self.nick_name}>'

    def get_mbti_choices(self):
        """選択した MBTI に応じた表示名称の選択肢を返す"""
        return self.MBTI_NAME_CHOICES.get(self.mbti, [])

    def get_mbti_name_display(self):
        """mbti_name のラベルを取得する"""
        for choices in self.MBTI_NAME_CHOICES.values():
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
    
    @property
    def get_profile_badges_icon(self):
        logger.info('start Profile get_profile_badges_icon')

        icon_url = staticfiles_storage.url('img/user.png')
        logger.debug(f'icon_url={icon_url}')
        badge_disp = self.badges or 'light'  # バッジがない場合はデフォルト
        logger.debug(f'badge_disp={badge_disp}')
        image_url = self.images.url if self.images else icon_url
        logger.debug(f'image_url={image_url}')
        nick_name = self.nick_name if self.nick_name else "Nick_Name"
        logger.debug(f'nick_name={nick_name}')

        html = f'''
        <span class="profile-icon badge d-inline-flex align-items-center justify-content-center p-0 pe-1 text-{badge_disp}-emphasis bg-{badge_disp}-subtle border border-{badge_disp}-subtle rounded-pill">
            <img class="rounded-circle me-1" width="24" height="24" src="{image_url}" alt="Profile icon">
            {nick_name}
        </span>
        '''
        logger.debug(f'html={html}')

        return html
    
    def save(self, *args, **kwargs):
        if self.images and self.images != self.__class__.objects.get(pk=self.pk).images: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            self.images = crop_square_image(self.images, 300) # Update the images size

        if self.themes and self.themes != self.__class__.objects.get(pk=self.pk).themes: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            self.themes = crop_16_9_image(self.themes, 1500) # Update the themes size

        """mbti_name が現在の mbti に対応しているかチェック"""
        if self.mbti and self.mbti_name:
            valid_choices = dict(self.MBTI_NAME_CHOICES.get(self.mbti, []))
            if self.mbti_name not in valid_choices:
                self.mbti_name = None  # 無効な場合はクリア

        super().save(*args, **kwargs)

    def get_all_groups(self):
        """ 所属しているすべてのグループを取得 """
        return self.groups.all()

    def get_group_profiles(self):
        """ 同じグループに所属する他のプロフィールを取得 """
        return Profile.objects.filter(groups__in=self.groups.all()).exclude(id=self.id).distinct()

    def get_chats(self):
        """ このプロフィールが作成したすべてのチャットを取得 """
        return self.chats.all()

    def get_chats_by_count(self, count=1):
        """ このプロフィールが作成した1週間以内のチャットから、直近の指定件数分のみを取得 """
        
        # 現在時刻から1週間前の日時を取得
        one_week_ago = timezone.now() - timedelta(days=7)

        # 1週間以内のチャットを取得し、指定件数分だけ表示
        return self.chats.filter(created_at__gte=one_week_ago).order_by('-created_at')[:count]

    def get_login_records(self, count=1):
        """ このプロフィールの1週間以内のログイン情報から、直近の指定件数分のみを取得 """

        # 現在時刻から1週間前の日時を取得
        one_week_ago = timezone.now() - timedelta(days=7)

        # 最新のログインで最新1件を抽出
        latest_unlogged = LoginRecord.objects.filter(
            user=self.user1).order_by('-login_time').first()

        # 1週間以内でログアウト済みのものを取得
        recent_logged = LoginRecord.objects.filter(
            user=self.user1,
            login_time__gte=one_week_ago,
            logout_time__isnull=False
        ).order_by('-login_time')[:count+1]

        # 結果をリストにして結合
        result = []

        # 最新の未ログアウトがある場合はリストに追加
        if latest_unlogged and not latest_unlogged.logout_time:
            result.append(latest_unlogged)

        # 残りのログアウト済み履歴を追加
        result.extend(recent_logged)

        # 指定件数でスライス（多すぎる場合に備えて）
        return result[:count]

    def get_friend_profiles(self):
        """
        自分の友達の Profile オブジェクトを取得。自分自身を除外。
        """
        # profile_id が profile1 側の場合 → profile2 を取得
        # profile_id が profile2 側の場合 → profile1 を取得
        from friend.models import Friend
        friends = Profile.objects.filter(
            Q(friends1__profile2_id=self.id) |  # 自分がprofile1側 → profile2を取得
            Q(friends2__profile1_id=self.id)    # 自分がprofile2側 → profile1を取得
        ).exclude(id=self.id).distinct()        # 自分を除外して重複を削除

        return friends

    @property
    def get_friend_pk(self):
        """
        ログイン中のユーザー（request.user.profile）と self profile が友達関係にある場合、
        対象のFriendオブジェクトのpkを返す。なければNone。
        :return: Friend.pk or None
        """
        request = get_current_request()
        if not request or not hasattr(request, 'user') or not hasattr(request.user, 'profile'):
            return None

        user_profile = request.user.profile

        from friend.models import Friend
        friend = Friend.objects.filter(
            Q(profile1=user_profile, profile2=self) |
            Q(profile1=self, profile2=user_profile)
        ).first()

        return friend.pk if friend else None

    def increment_given_likes(self):
        # 一旦、常にインクリメント
        self.given_likes += 1
        self.save()

        return self.given_likes

    def is_status_in(self):
        """
        このプロフィールの最新のチェックインレコードを取得し、
        当日チェックインしていて、かつチェックアウトしていない場合にTrueを返す。
        """
        from place.models import CheckinRecord
        today = date.today()  # 今日の日付
        # 最新のチェックインレコードを取得
        latest_checkin = CheckinRecord.objects.filter(profile=self).order_by('-checkin_time').first()

        if latest_checkin:
            # 最新のチェックインが当日であり、かつ、チェックアウト時間がnullならTrue
            if latest_checkin.checkin_time.date() == today and latest_checkin.checkout_time is None:
                return True

        return False

class LoginRecord(models.Model):
    """ログイン履歴"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='User', on_delete=models.PROTECT)
    login_time = models.DateTimeField('Login', blank=True, null=True)
    logout_time = models.DateTimeField('Logout', blank=True, null=True)

    def __str__(self):
        login_dt = timezone.localtime(self.login_time)
        return '{0} - {1.year}/{1.month}/{1.day} {1.hour}:{1.minute}:{1.second} - {2}'.format(
            self.user.username, login_dt, self.get_diff_time()
        )

    def get_diff_time(self):
        """ログアウト時間ーログイン時間"""
        if not self.logout_time:
            return 'In'
        else:
            td = self.logout_time - self.login_time
            hours, remainder = divmod(td.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f'{hours:02}:{minutes:02}'
                

@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    """ログインした際に呼ばれる"""
    LoginRecord.objects.create(user=user, login_time=timezone.now())


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    """ログアウトした際に呼ばれる"""
    try:
        record = LoginRecord.objects.filter(user=user, logout_time__isnull=True).latest('pk')
        record.logout_time = timezone.now()
        record.save()
    except LoginRecord.DoesNotExist:
        pass
