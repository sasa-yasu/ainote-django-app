import random  # ← ランダム数生成用
from django.db import models
from django.utils import timezone
from django.db.models import F
from AinoteProject.utils import crop_square_image, crop_16_9_image
from user.models import Profile

class Device(models.Model):
    """Device entity representing a registered product."""
    name = models.CharField('Name', max_length=100, null=True, blank=True)
    images = models.ImageField('Images', upload_to='device', null=True, blank=True)
    themes = models.ImageField('Themes', upload_to='device', null=True, blank=True)
    maker = models.CharField('Maker', max_length=100, null=True, blank=True)
    productno = models.CharField('ProductNo', max_length=100, null=True, blank=True)
    context = models.TextField('Context', null=True, blank=True)
    remarks = models.TextField('Remarks', null=True, blank=True)
    schedule_monthly = models.CharField('Schedule Monthly', max_length=1024, null=True, blank=True)
    schedule_weekly = models.CharField('Schedule Weekly', max_length=1024, null=True, blank=True)
    likes = models.IntegerField(null=True, blank=True, default=0)
    likes_record =  models.TextField(null=True, blank=True, default='|')
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    created_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='device_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField('Updated at', auto_now=True)
    updated_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='device_updated_pics')  # 紐づくProfileが削除されたらNULL設定

    def __str__(self):
        return f'<Device:id={self.id}, name={self.name}>'

    def save(self, *args, **kwargs):
        
        # 新規作成時に `likes` にランダム数を割り当てる
        if self._state.adding and self.likes is None:
            self.likes = random.randint(1, 5)

        # 画像処理
        try:
            orig = self.__class__.objects.get(pk=self.pk)
        except self.__class__.DoesNotExist:
            orig = None

        if self.images and orig and self.images != orig.images: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            self.images = crop_square_image(self.images, 300) # Update the images size

        if self.themes and orig and self.themes != orig.themes: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            self.themes = crop_16_9_image(self.themes, 1500) # Update the themes size

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
            Device.objects.filter(pk=self.pk).update(likes=F('likes') + 1)
            self.refresh_from_db()

            # given_likesをインクリメント
            try:
                profile = Profile.objects.get(user1=request.user)
                profile.increment_given_likes()
            except Profile.DoesNotExist:
                pass

        return self.likes
