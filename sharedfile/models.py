import random  # ← ランダム数生成用
from django.db import models
from django.utils import timezone
from multiselectfield import MultiSelectField
from AinoteProject.utils import crop_square_image, crop_16_9_image
from user.models import Profile

class SharedFile(models.Model):
    title = models.CharField('Title', max_length=255, null=True, blank=True)
    images = models.ImageField('Images', upload_to='sharedfile', null=True, blank=True)
    themes = models.ImageField('Themes', upload_to='sharedfile', null=True, blank=True)

    CATEGORY_CHOICES = [
        # ① 生徒管理系
        ('student_roster', '🧑‍🎓生徒名簿管理表📋'),
        ('student_notes', '📖個別指導カルテ📝'),
        ('attendance', '⏰出席・欠席管理表🚪'),

        # ② 成績・学習記録系
        ('test_scores', '📊テスト結果記録・分析表🧪'),
        ('score_trends', '📈成績推移グラフツール📉'),
        ('understanding_check', '✅単元別理解度チェックシート🔍'),

        # ③ スケジュール・運営系
        ('timetable', '🗓️時間割・講師シフト表👨‍🏫'),
        ('lesson_schedule', '📆授業スケジュール管理表📝'),
        ('contact_log', '📞保護者連絡記録表🗒️'),

        # ④ 宿題・教材管理系
        ('homework_check', '📚宿題提出チェック表✏️'),
        ('material_progress', '📘教材進捗管理表📏'),

        # ⑤ 進路指導系
        ('exam_plan', '🎯受験校リスト管理表🏫'),
        ('success_record', '🏆合格実績集計ツール📜'),
        ('interview_log', '💬面談記録シート🧾'),

        # ⑥ 分析・報告資料系
        ('report_template', '🖨️保護者会資料作成テンプレート📑'),
        ('class_report', '📋クラス別成績レポート自動集計📐'),

        # その他
        ('others', '🧰その他🗂️'),
    ]
    category_choice = MultiSelectField('Category Choice', max_length=200, choices=CATEGORY_CHOICES, null=True, blank=True) 

    files = models.FileField(upload_to='sharedfile', null=True, blank=True)

    overview = models.TextField('Overview', null=True, blank=True)
    context = models.TextField('Context', null=True, blank=True)

    remarks = models.TextField('Remarks', null=True, blank=True)
    likes = models.IntegerField(null=True, blank=True)
    likes_record =  models.TextField(null=True, blank=True, default = '|')

    created_at = models.DateTimeField(auto_now_add=True)
    created_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='sharedfile_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField(auto_now=True)
    updated_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='sharedfile_updated_pics')  # 紐づくProfileが削除されたらNULL設定

    def __str__(self):
        return f'<SharedFile:id={self.id}, {self.title}>'

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
