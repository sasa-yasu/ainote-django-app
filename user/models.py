import logging
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models import Q, F
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
    memberid = models.CharField('Member Id', max_length=100, null=True, blank=True)
    nick_name = models.CharField('Nick Name', max_length=10, null=True, blank=True)
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

    default_year = timezone.now().year  # 当年を基準にして選択肢を作成
    years_choice = [(year, str(year)) for year in range(default_year - 130, default_year + 1)]  # 過去130年分の年をリストとして作成
    birth_year = models.PositiveIntegerField('Birthday(Y)', choices=years_choice, null=True, blank=True)  # 年を保存

    birth_month_day = models.DateField('Birth(M/D))', null=True, blank=True)  # 月日を保存、デフォルトは12月31日

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

    CONTRACT_COURSE_CHOICES = [
        ('-', '-'),
        ('trial', 'トライアル会員(1ヶ月2日間のみ)'),
        ('bronze', 'ブロンズ会員(1ヶ月5日間のみ)'),
        ('gold', 'ゴールド会員(1ヶ月10日間のみ)'),
        ('platinum', 'プラチナ会員(1ヶ月何度でも利用可能)'),
        ('premium', 'プレミアム会員(ゴールド会員特典＋全コース受講可)'),
    ]
    contract_course = models.CharField('Contract Course', max_length=100, choices=CONTRACT_COURSE_CHOICES, null=True, blank=True)

    caretaker01 = models.CharField('Caretaker01 email', max_length=255, null=True, blank=True)
    caretaker02 = models.CharField('Caretaker02 email', max_length=255, null=True, blank=True)
    caretaker03 = models.CharField('Caretaker03 email', max_length=255, null=True, blank=True)
    caretaker04 = models.CharField('Caretaker04 email', max_length=255, null=True, blank=True)
    caretaker05 = models.CharField('Caretaker05 email', max_length=255, null=True, blank=True)

    status_points = models.IntegerField(null=True, blank=True, default=0)
    available_points = models.IntegerField(null=True, blank=True, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    created_pic = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField(auto_now=True)
    updated_pic = models.ForeignKey('Profile', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_updated_pics')  # 紐づくProfileが削除されたらNULL設定

    """ グループモデル """
    groups = models.ManyToManyField('group.Group', blank=True, related_name='group_profiles')  # 紐づくProfileが削除されてもChatは残る

    """ スレッドモデル """
    threads = models.ManyToManyField('thread.Thread', blank=True, related_name='thread_profiles')  # 紐づくProfileが削除されてもChatは残る

    class Meta:
        pass

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

    def got_points_for_checkin(self):
        self.status_points += 1
        self.available_points += 1
        self.save()

        return self.status_point

    def got_points_for_make_friend(self):
        self.status_points += 1
        self.available_points += 1
        self.save()

        return self.status_points

    def lost_points_for_remove_friend(self):
        self.status_points -= 1
        self.available_points -= 1
        self.save()

        return self.status_points

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

    def get_classification_value(self):
        """年齢に基づく世代分類値を返す"""
        if not self.birth_year:
            return 0 # if not register the birth year, can get NO point.

        # 誕生日を考慮した実際の年齢（満年齢）を返す 月日が入っていない場合は12/31を採用
        try:
            month = self.birth_month_day.month
            day = self.birth_month_day.day
            birth_date = date(self.birth_year, month, day)
        except ValueError:
            # フォールバック：月日が不正なら12/31を仮定
            birth_date = date(self.birth_year, 12, 31)

        today = date.today()
        age = today.year - birth_date.year

        # 誕生日がまだ来ていなければ1歳引く
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1

        if   age <=   5:    return 1
        elif age <=   8:    return 2
        elif age <=  11:    return 3
        elif age <=  14:    return 4
        elif age <=  17:    return 5
        elif age <=  21:    return 6
        elif age <=  29:    return 7
        elif age <=  39:    return 8
        elif age <=  49:    return 9
        elif age <=  59:    return 10
        elif age <=  69:    return 11
        elif age <=  79:    return 12
        elif age <=  89:    return 13
        elif age <=  99:    return 14
        elif age <= 109:    return 15
        elif age <= 119:    return 16
        else:               return 17

    def get_earn_points_for_make_friend(self, friend):
        """友達関係によりポイントを付与する（相手との世代差に応じて）"""

        # 世代差を計算
        my_value = self.get_classification_value()
        friend_value = friend.get_classification_value()

        if my_value == 0 or friend_value == 0: # if either one is 0(not register year). can get NO point.
            return 0
        
        diff = abs(my_value - friend_value)

        # ポイント決定
        earn_points = diff
    
        return earn_points

    def earn_points_for_make_friend(self, friend):

        if not self.is_friends_with(friend):
            return  0 # まだ友達でないなら何もしない

        # profile1 < profile2 の順に並び替え
        profile1, profile2 = sorted([self, friend], key=lambda p: p.id)

        # すでにポイントが付与済みかチェック（重複防止）
        if FriendshipPointLog.objects.filter(profile1=profile1, profile2=profile2, reward_returned=False).exists():
            return 0 

        earn_points = self.get_earn_points_for_make_friend(friend)
        
        # ポイント加算
        self.status_points += earn_points
        self.available_points += earn_points
        self.save()
        friend.status_points += earn_points
        friend.available_points += earn_points
        friend.save()

        # ログ記録（重複加算防止）
        FriendshipPointLog.objects.create(profile1=profile1, profile2=profile2, points_awarded=earn_points)

        return self.status_points

    def get_lose_points_for_remove_friend(self, friend):
        """友達関係によりポイントを付与する（相手との世代差に応じて）"""

        # profile1 < profile2 の順に並び替え
        profile1, profile2 = sorted([self, friend], key=lambda p: p.id)

        # すでにポイントが付与済みかチェック：ポイント付与履歴がなければ減算もなし
        if not FriendshipPointLog.objects.filter(profile1=profile1, profile2=profile2, reward_returned=False).exists():
            return 0

        friendship_point_log = FriendshipPointLog.objects.filter(profile1=profile1, profile2=profile2, reward_returned=False).first()
    
        return friendship_point_log.points_awarded

    def lose_points_for_remove_friend(self, friend):

        if not self.is_friends_with(friend):
            return  0 # まだ友達でないなら何もしない

        # profile1 < profile2 の順に並び替え
        profile1, profile2 = sorted([self, friend], key=lambda p: p.id)

        # すでにポイントが付与済みかチェック：ポイント付与履歴がなければ減算もなし
        if not FriendshipPointLog.objects.filter(profile1=self, profile2=friend, reward_returned=False).exists():
            return 0

        friendship_point_log = FriendshipPointLog.objects.filter(profile1=profile1, profile2=profile2, reward_returned=False).first()

        lose_points = friendship_point_log.points_awarded

        # ポイント減算
        self.status_points -= lose_points
        self.available_points -= lose_points
        self.save()
        friend.status_points -= lose_points
        friend.available_points -= lose_points
        friend.save()

        # ログ記録（重複減算防止）
        friendship_point_log.reward_returned = True
        friendship_point_log.save()

        return self.status_points

    def is_friends_with(self, other):
        """相互友達関係であるかどうかを判定"""
        from friend.models import Friend
        return Friend.objects.filter( Q(profile1=self, profile2=other) | Q(profile1=other, profile2=self) ).exists()

    STATUS_POINTS_PRIZE_CHOICES = [
        (50, 'Wood(木)', 'wood'),
        (100, 'Bamboo(竹)', 'bamboo'),
        (200, 'Iron(鉄)', 'iron'),
        (350, 'Bronze(銅)', 'bronze'),
        (600, 'Carbon(ｶｰﾎﾞﾝ)', 'carbon'),
        (1000, 'Titan(ﾁﾀﾝ)', 'titan'),
        (1800, 'Silver(ｼﾙﾊﾞｰ)', 'silver'),
        (3000, 'Gold(ｺﾞｰﾙﾄﾞ)', 'gold'),
        (9999, 'Platinum(ﾌﾟﾗﾁﾅ)', 'platinum'),
    ]

    def get_status_points_prize(self):
        # status_pointsに基づいて該当する賞品を選択
        for threshold, prize_name, prize_code in reversed(Profile.STATUS_POINTS_PRIZE_CHOICES):
            if self.status_points >= threshold:
                return prize_name
        return 'Wood(ｳｯﾄﾞ)'  # デフォルトは 'Wood(ｳｯﾄﾞ)' としておく

    def get_status_points_prize_code(self):
        # status_pointsに基づいて該当する賞品を選択
        for threshold, prize_name, prize_code in reversed(Profile.STATUS_POINTS_PRIZE_CHOICES):
            if self.status_points >= threshold:
                return prize_name
        return 'wood'  # デフォルトは 'wood' としておく

class LoginRecord(models.Model):
    """ログイン履歴"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='User', on_delete=models.CASCADE)
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


class FriendshipPointLog(models.Model):
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friend_point_logs1')
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friend_point_logs2')
    points_awarded = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    reward_returned = models.BooleanField(default=False)

    class Meta:
        unique_together = ('profile1', 'profile2', 'created_at')  # 同時刻同じペアでの重複防止（必要に応じて）
        constraints = [
            models.CheckConstraint(
                check = Q( profile1_id__lt=F('profile2_id') ),
                name = 'check_profile_order_in_log'
            )
        ]

    def __str__(self):
        return f"<PointLog:{self.profile1} - {self.profile2} +{self.points_awarded}pt @ {self.created_at}>"

