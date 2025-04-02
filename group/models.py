import random  # ← ランダム数生成用
from django.db import models
from django.utils import timezone
from AinoteProject.utils import crop_square_image, crop_16_9_image
from user.models import Profile

class Group(models.Model):
    """Group"""
    name = models.CharField('Name', max_length=255, null=True, blank=True)
    images = models.ImageField('Images', upload_to='group', null=True, blank=True)
    themes = models.ImageField('Themes', upload_to='group', null=True, blank=True)
    context = models.TextField('Context', null=True, blank=True)
    remarks = models.TextField('Remarks', null=True, blank=True)
    likes = models.IntegerField(null=True, blank=True)
    likes_record =  models.TextField(null=True, blank=True, default = '|')
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id'], name='group_pk'),
        ]

    def __str__(self):
        return f'<Group:id={self.id}, {self.name}>'

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
        return self.profiles.all()

    def get_all_groups_profiles(self):
        """ Profileに紐づいているすべてのグループ情報をProfile情報付きで取得 """
        return self.objects.prefetch_related('profiles').all()

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
