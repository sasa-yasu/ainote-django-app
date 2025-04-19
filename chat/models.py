import random  # ← ランダム数生成用
from django.db import models
from AinoteProject.utils import crop_square_image
from django.utils import timezone
from django.db.models import F
from user.models import Profile

# Create your models here.
class Chat(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    context = models.TextField(null=True, blank=True)
    images = models.ImageField(upload_to='chat', null=True, blank=True)
    author = models.CharField(max_length=100, null=True, blank=True)
    likes = models.IntegerField(null=True, blank=True, default=0)
    likes_record =  models.TextField(null=True, blank=True, default='|')
    order_by_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField(auto_now=True)
    updated_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_updated_pics')  # 紐づくProfileが削除されたらNULL設定

    """ Profile紐づけ """
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='chats')  # 紐づくProfileが削除されてもChatは残る

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
        if self.pk:
            orig = self.__class__.objects.filter(pk=self.pk).first()
            if self.images and orig and self.images != orig.images: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
                self.images = crop_square_image(self.images, 300) # Update the images size

        super().save(*args, **kwargs)

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
            Chat.objects.filter(pk=self.pk).update(likes=F('likes') + 1)
            self.refresh_from_db()

            # given_likesをインクリメント
            profile = Profile.objects.get(user1=request.user)
            profile.increment_given_likes()

        return self.likes

    def age_order_by_at(self, request):
        if request.user and request.user.is_authenticated:
            # order_by_atに現在日時を設定してリストの一番上に上げる
            self.order_by_at = timezone.now()
            self.save()

            # given_likesをインクリメント
            profile = Profile.objects.get(user1=request.user)
            profile.increment_given_likes()

        return self.order_by_at
