import random  # ← ランダム数生成用
from django.db import models
from django.utils import timezone
from middleware.current_request import get_current_request
from multiselectfield import MultiSelectField
from AinoteProject.utils import crop_square_image, crop_16_9_image
from user.models import Profile

class Thread(models.Model):
    """Thread"""
    name = models.CharField('Name', max_length=255, null=True, blank=True)
    images = models.ImageField('Images', upload_to='thread', null=True, blank=True)
    themes = models.ImageField('Themes', upload_to='thread', null=True, blank=True)
    CATEGORY_CHOICES = [
        ('general_gaming', '🎮ゲーム好き集合！🧑‍💻'),
        ('battle_gaming', '⚔️バトル＆対戦好き集まれ🔥'),
        ('thrill_games', '👻ゾクゾクするゲーム体験🎢'),
        ('indie_games', '🕹️インディーズゲーム発掘隊🔍'),
        ('sports_fans', '🏀スポーツファン交流所🏃‍♂️'),
        ('oshi_talk', '🌟推し活・アイドルトーク💖'),
        ('entertainment_talk', '🎬エンタメ雑談広場🎉'),
        ('story_world', '📚創作・物語・世界観好き🌌'),
        ('philosophy_talk', '🧠知的＆哲学系トーク📖'),
        ('recommendations', '📢みんなのおすすめ紹介所📝'),
        ('free_talk', '💬なんでも雑談ルーム🕊️'),
    ]
    category_choice = MultiSelectField('Category Choice', max_length=200, choices=CATEGORY_CHOICES, null=True, blank=True) 
    overview = models.TextField('Overview', null=True, blank=True)
    context = models.TextField('Context', null=True, blank=True)
    remarks = models.TextField('Remarks', null=True, blank=True)
    likes = models.IntegerField(null=True, blank=True)
    likes_record =  models.TextField(null=True, blank=True, default = '|')
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    created_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='thread_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField('Updated at', auto_now=True)
    updated_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='thread_updated_pics')  # 紐づくProfileが削除されたらNULL設定

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id'], name='thread_pk'),
        ]

    def __str__(self):
        return f'<Thread:id={self.id}, {self.name}>'

    def save(self, *args, **kwargs):
        # 新規作成時に `likes` にランダム数を割り当てる
        if self._state.adding and self.likes is None:
            self.likes = random.randint(1, 5)

        # 画像処理
        if self.images and self.images != self.__class__.objects.get(pk=self.pk).images: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            self.images = crop_square_image(self.images, 300) # Update the images size

        # 画像処理
        if self.themes and self.themes != self.__class__.objects.get(pk=self.pk).themes: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            self.themes = crop_16_9_image(self.themes, 1500) # Update the themes size

        super().save(*args, **kwargs)

    def get_profiles(self):
        """ グループに所属するすべてのプロフィールを取得 """
        return self.thread_profiles.all()

    @property
    def is_user_member(self):
        """
        request.userがこのThreadに所属していればTrueを返す
        """
        request = get_current_request()  # 現在のリクエストを取得
        if not request.user.is_authenticated:
            return False

        try:
            user_profile = request.user.profile
        except Profile.DoesNotExist:
            return False

        return self.thread_profiles.filter(id=user_profile.id).exists()

    def get_all_threads_profiles(self):
        """ Profileに紐づいているすべてのグループ情報をProfile情報付きで取得 """
        return self.objects.prefetch_related('thread_profiles').all()

    def push_likes(self, request):
        if request.user:
            now = timezone.now()
            formatted_date = now.strftime("%y%m%d") # formatting: "YYMMDD" "250304"）
            CheckKey = f'{formatted_date}-{str(request.user.id)}|'

            if not CheckKey in self.likes_record: # Same YMDHM then No Increment
                if self.likes is None:
                    self.likes = random.randint(1, 5)  # 念のため初期化チェック
                self.likes_record += CheckKey
                #self.likes += 1

            # 一旦、常にlikesをインクリメント
            self.likes += 1

            self.save()

            # given_likesをインクリメント
            profile = Profile.objects.get(user1=request.user)
            profile.increment_given_likes()

        return self.likes

# Create your models here.
class ThreadChat(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    context = models.TextField(null=True, blank=True)
    images = models.ImageField(upload_to='thread/chat', null=True, blank=True)
    author = models.CharField(max_length=100, null=True, blank=True)
    likes = models.IntegerField(null=True, blank=True)
    likes_record =  models.TextField(null=True, blank=True, default = '|')
    order_by_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='thread_chat_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField(auto_now=True)
    updated_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='thread_chat_updated_pics')  # 紐づくProfileが削除されたらNULL設定

    """ Profile紐づけ """
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='profile2thread_chats')  # 紐づくProfileが削除されてもChatは残る

    # additional
    """ Thread紐づけ """
    thread = models.ForeignKey(Thread, on_delete=models.SET_NULL, null=True, blank=True, related_name='thread2chats' )  # 紐づくProfileが削除されてもThreadは残る

    class Meta:
        pass

    def __str__(self):
        return f"{self.title} <by { self.author if self.author else 'Unknown' }>"

    def save(self, *args, **kwargs):
        # 新規作成時に `order_by_at` にnowを設定
        if self._state.adding:
            self.order_by_at = timezone.now()

        # 新規作成時に `likes` にランダム数を割り当てる
        if self._state.adding and self.likes is None:
            self.likes = random.randint(1, 5)

        # 画像処理
        if self.images and self.images != self.__class__.objects.get(pk=self.pk).images: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            self.images = crop_square_image(self.images, 300) # Update the images size

        super().save(*args, **kwargs)

    def push_likes(self, request):
        if request.user:
            now = timezone.now()
            formatted_date = now.strftime("%y%m%d") # formatting: "YYMMDD" "250304"）
            CheckKey = f'{formatted_date}-{str(request.user.id)}|'

            if not CheckKey in self.likes_record: # Same YMDHM then No Increment
                if self.likes is None:
                    self.likes = random.randint(1, 5)  # 念のため初期化チェック
                self.likes_record += CheckKey
                #self.likes += 1

            # 一旦、常にlikesをインクリメント
            self.likes += 1

            self.save()

            # given_likesをインクリメント
            profile = Profile.objects.get(user1=request.user)
            profile.increment_given_likes()

        return self.likes

    def age_order_by_at(self, request):
        if request.user:
            # order_by_atに現在日時を設定してリストの一番上に上げる
            self.order_by_at = timezone.now()
            self.save()

            # given_likesをインクリメント
            profile = Profile.objects.get(user1=request.user)
            profile.increment_given_likes()

        return self.order_by_at
