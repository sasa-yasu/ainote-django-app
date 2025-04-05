import random  # ← ランダム数生成用
from django.db import models
from django.utils import timezone
from AinoteProject.utils import resize_image, crop_16_9_image
from django.conf import settings
from datetime import timedelta
from django.db.models import Max
from django.db.models.functions import TruncDate
from user.models import Profile

class Place(models.Model):
    """Place"""
    place = models.CharField('Place', max_length=100, null=True, blank=True)
    images = models.ImageField('Images', upload_to='place', null=True, blank=True)
    themes = models.ImageField('Themes', upload_to='place', null=True, blank=True)
    area = models.CharField('Area', max_length=100, null=True, blank=True)
    overview = models.TextField('Overview', null=True, blank=True)
    address = models.CharField('Address', max_length=255, null=True, blank=True)
    tel = models.CharField('Tel', max_length=100, null=True, blank=True)
    url = models.URLField('URL', max_length=500, null=True, blank=True)
    context = models.TextField('Context', null=True, blank=True)
    remarks = models.TextField('Remarks', null=True, blank=True)
    likes = models.IntegerField(null=True, blank=True)
    likes_record =  models.TextField(null=True, blank=True, default = '|')
    schedule_monthly = models.CharField('Schedule Monthly', max_length=1028, null=True, blank=True)
    schedule_weekly = models.CharField('Schedule Weekly', max_length=1028, null=True, blank=True)

    # GPS 座標を追加
    latitude = models.FloatField('Latitude', null=True, blank=True)
    longitude = models.FloatField('Longitude', null=True, blank=True)
    googlemap_url = models.CharField('Google Map URL', max_length=3000, null=True, blank=True)

    created_at = models.DateTimeField('Created at', auto_now_add=True)
    created_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='place_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField('Updated at', auto_now=True)
    updated_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='place_updated_pics')  # 紐づくProfileが削除されたらNULL設定

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id'], name='place_pk'),
        ]

    def __str__(self):
        return f'<Place:id={self.id}, {self.place}, {self.area}>'

    def save(self, *args, **kwargs):

        # 新規作成時に `likes` にランダム数を割り当てる
        if self._state.adding and self.likes is None:
            self.likes = random.randint(1, 5)
            
        if self.images and self.images != self.__class__.objects.get(pk=self.pk).images: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            self.images = resize_image(self.images, 300) # Update the images size

        if self.themes and self.themes != self.__class__.objects.get(pk=self.pk).themes: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            self.themes = crop_16_9_image(self.themes, 1500) # Update the themes size

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

    def get_checkin_records_by_count(self, count=1):
        """
        同じプロフィールで同日付(Y/M/D)のチェックインレコードは最終PKのみ取得。
        直近1週間分のチェックイン記録を取得。
        """
        
        # 現在時刻から1週間前の日時を取得
        one_week_ago = timezone.now() - timedelta(days=7)

        # 同一Profileと同日付で最大PKを取得
        latest_pks = (
            self.checkinrecord_set
            .filter(checkin_time__gte=one_week_ago)
            .annotate(date=TruncDate('checkin_time'))  # 日付でグループ化
            .values('profile_id', 'date')  # Profileごとに日付でグループ化
            .annotate(latest_pk=Max('pk'))  # 各グループ内で最大PK取得
            .values_list('latest_pk', flat=True)
        )

        # 最新の指定件数分のみ取得
        return (
            self.checkinrecord_set
            .filter(pk__in=latest_pks)
            .select_related('profile')
            .order_by('-pk')[:count]
        )

    def get_checkin_status(self):
        """
        同じプロフィールで同日付(Y/M/D)のチェックインレコードは最終PKのみ取得。
        checkout_timeが入っていないレコードのみ取得。
        """
        
        # 現在時刻から1週間前の日時を取得
        one_week_ago = timezone.now() - timedelta(days=7)

        # 同一Profileと同日付でcheckout_timeがない最新PKを取得
        latest_pks = (
            self.checkinrecord_set
            .filter(checkin_time__gte=one_week_ago, checkout_time__isnull=True)  # チェックアウトがないもの
            .annotate(date=TruncDate('checkin_time'))  # 日付でグループ化
            .values('profile_id', 'date')  # Profileごとに日付でグループ化
            .annotate(latest_pk=Max('pk'))  # 各グループ内で最大PK取得
            .values_list('latest_pk', flat=True)
        )

        # 最新PKのレコードのみ取得
        return (
            self.checkinrecord_set
            .filter(pk__in=latest_pks)
            .select_related('profile')
            .order_by('-pk')
        )


class CheckinRecord(models.Model):
    """チェックイン履歴"""

    place = models.ForeignKey(
        Place, verbose_name='Place', on_delete=models.PROTECT)
    profile = models.ForeignKey(
        Profile, verbose_name='Profile', on_delete=models.PROTECT)
    checkin_time = models.DateTimeField('Checkin', blank=True, null=True)
    checkout_time = models.DateTimeField('Checkout', blank=True, null=True)

    def __str__(self):
        return '{0} - {1} -{2.year}/{2.month}/{2.day} {2.hour}:{2.minute}:{2.second} - {3}'.format(
            self.place.place, self.profile.user1.username, self.checkin_time, self.get_diff_time()
        )

    def get_diff_time(self):
        """チェックアウト時間ーチェックイン時間"""
        if not self.checkout_time:
            return 'In'
        else:
            td = self.checkout_time - self.checkin_time
            hours, remainder = divmod(td.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f'{hours:02}:{minutes:02}'
