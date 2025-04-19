import random  # ← ランダム数生成用
from django.db import models
from django.utils import timezone
from django.db.models import F
from middleware.current_request import get_current_request
from multiselectfield import MultiSelectField
from AinoteProject.utils import crop_square_image, crop_16_9_image
from user.models import Profile

class Group(models.Model):
    """Group"""
    name = models.CharField('Name', max_length=255, null=True, blank=True)
    images = models.ImageField('Images', upload_to='group', null=True, blank=True)
    themes = models.ImageField('Themes', upload_to='group', null=True, blank=True)
    CATEGORY_CHOICES = [
        ('sports', '⚽スポーツ🏃‍♀️'),
        ('walking', '🚶‍♂️歩活（ウォーキング）🌳'),
        ('bbq', '🍖バーベキュー🔥'),
        ('music', '🎵音楽・演奏🎸'),
        ('study', '📚勉強会・学習🧠'),
        ('hobby', '🎨趣味・創作✂️'),
        ('childcare', '🍼子育てサークル👶'),
        ('volunteer', '🤝ボランティア👐'),
        ('intergenerational', '👨‍👩‍👧‍👦世代交流🕊️'),
        ('community', '🏘️地域活動👫'),
        ('other', '🧩その他🗂️'),
    ]
    category_choice = MultiSelectField('Category Choice', max_length=200, choices=CATEGORY_CHOICES, null=True, blank=True) 
    context = models.TextField('Context', null=True, blank=True)
    remarks = models.TextField('Remarks', null=True, blank=True)
    schedule_monthly = models.CharField('Schedule Monthly', max_length=1024, null=True, blank=True)
    schedule_weekly = models.CharField('Schedule Weekly', max_length=1024, null=True, blank=True)
    task_control = models.CharField('Task Control', max_length=1024, null=True, blank=True)
    likes = models.IntegerField(null=True, blank=True, default=0)
    likes_record =  models.TextField(null=True, blank=True, default='|')
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    created_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='group_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField('Updated at', auto_now=True)
    updated_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='group_updated_pics')  # 紐づくProfileが削除されたらNULL設定

    def __str__(self):
        return f'<Group:id={self.id}, {self.name}>'

    def save(self, *args, **kwargs):
        # 新規作成時に `likes` にランダム数を割り当てる
        if self._state.adding and self.likes is None:
            self.likes = random.randint(1, 5)

        # 画像処理
        if self.pk:
            orig = self.__class__.objects.filter(pk=self.pk).first()
            if self.images and orig and self.images != orig.images: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
                self.images = crop_square_image(self.images, 300) # Update the images size

            if self.themes and orig and self.themes != orig.themes: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
                self.themes = crop_16_9_image(self.themes, 1500) # Update the themes size

        super().save(*args, **kwargs)

    def get_profiles(self):
        """ グループに所属するすべてのプロフィールを取得 """
        return self.group_profiles.all()

    @property
    def is_user_member(self):
        """
        request.userがこのGroupに所属していればTrueを返す
        """
        request = get_current_request()  # 現在のリクエストを取得
        if not request.user.is_authenticated:
            return False

        try:
            user_profile = request.user.profile
        except Profile.DoesNotExist:
            return False

        return self.group_profiles.filter(id=user_profile.id).exists()

    def get_all_groups_profiles(self):
        """ Profileに紐づいているすべてのグループ情報をProfile情報付きで取得 """
        return self.objects.prefetch_related('grou_profiles').all()

    def push_likes(self, request):
        if request.user and request.user.is_authenticated:
            now = timezone.now()
            formatted_date = now.strftime("%y%m%d") # formatting: "YYMMDD" "250304"）
            CheckKey = f'{formatted_date}-{str(request.user.id)}|'

            if not CheckKey in self.likes_record: # Same YMDHM then No Increment
                if self.likes is None:
                    self.likes = random.randint(1, 5)  # 念のため初期化チェック
                self.likes_record += CheckKey
                #self.likes += 1

            # 一旦、常にlikesをインクリメント
            Group.objects.filter(pk=self.pk).update(likes=F('likes') + 1)
            self.refresh_from_db()

            # given_likesをインクリメント
            try:
                profile = Profile.objects.get(user1=request.user)
                profile.increment_given_likes()
            except Profile.DoesNotExist:
                pass

        return self.likes
