from django.db import models
from django.utils import timezone
from user.models import Profile

# Create your models here.
# Friendモデル
class Friend(models.Model):
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friends1')
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friends2')
    created_at = models.DateTimeField(default=timezone.now)
    created_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='friend_created_pics')  # 紐づくProfileが削除されたらNULL設定

    class Meta:
        # 同一関係を防ぐために一意制約を追加
        unique_together = ('profile1', 'profile2')
        constraints = [
            models.CheckConstraint(
                check=models.Q(profile1_id__lt=models.F('profile2_id')),
                name='check_profile_order'  # profile1_id < profile2_id の制約
            )
        ]

    def __str__(self):
        return f'<Friend:id={self.id}, {self.profile1} - {self.profile2}'
