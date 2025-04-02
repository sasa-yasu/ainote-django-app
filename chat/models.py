import random  # ← ランダム数生成用
from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone
from user.models import Profile

# Create your models here.
class Chat(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    context = models.TextField(null=True, blank=True)
    images = models.ImageField(upload_to='chat', null=True, blank=True)
    author = models.CharField(max_length=100, null=True, blank=True)
    likes = models.IntegerField(null=True, blank=True)
    likes_record =  models.TextField(null=True, blank=True, default = '|')
    order_by_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    """ Profile紐づけ """
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='chats' )  # 紐づくProfileが削除されてもChatは残る

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id'], name='chat_pk'),
        ]

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
            img = Image.open(self.images)
            format = img.format if img.format else "JPEG"  # フォーマットがない場合はJPEGで保存

            max_size = (300, 300)
            img.thumbnail(max_size)  # keep height x width shape

            img_io = BytesIO() # prepare buffer area
            print(f'images img.format={img.format}')
            img.save(img_io, format=format) # save to buffer area

            self.images = ContentFile(img_io.getvalue(), name=self.images.name) # Update the images size

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