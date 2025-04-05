from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from user.models import Profile

class Notice(models.Model):
    """Notice"""
    images = models.ImageField('Images', upload_to='notice', null=True, blank=True)
    title = models.CharField('Title', max_length=255, null=True, blank=True)
    period = models.CharField('Period', max_length=255, null=True, blank=True)
    overview = models.TextField('Overview', null=True, blank=True)
    context = models.TextField('Context', null=True, blank=True)
    published_at = models.DateField('Published at', null=True, blank=True)
    remarks = models.TextField('Remarks', null=True, blank=True)
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    created_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='notice_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField('Updated at', auto_now=True)
    updated_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='notice_updated_pics')  # 紐づくProfileが削除されたらNULL設定

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['id'], name='notice_pk'),
        ]

    def __str__(self):
        return f'<Notice:id={self.id}, {self.name}>'

    def save(self, *args, **kwargs):
        if self.images and self.images != self.__class__.objects.get(pk=self.pk).images: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
            img = Image.open(self.images)
            format = img.format if img.format else "JPEG"  # フォーマットがない場合はJPEGで保存

            max_size = (500, 500)
            img.thumbnail(max_size)  # keep height x width shape

            img_io = BytesIO() # prepare buffer area
            print(f'images img.format={img.format}')
            img.save(img_io, format=format) # save to buffer area

            self.images = ContentFile(img_io.getvalue(), name=self.images.name) # Update the images size

        super().save(*args, **kwargs)
    
