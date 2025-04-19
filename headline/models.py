from django.db import models
from AinoteProject.utils import crop_square_image, crop_16_9_image
from user.models import Profile

class Headline(models.Model):
    """Headline"""
    images = models.ImageField('Images', upload_to='headline', null=True, blank=True)
    title = models.CharField('Title', max_length=255, null=True, blank=True)
    period = models.CharField('Period', max_length=255, null=True, blank=True)
    overview = models.TextField('Overview', null=True, blank=True)
    context = models.TextField('Context', null=True, blank=True)
    published_at = models.DateField('Published at', null=True, blank=True)
    remarks = models.TextField('Remarks', null=True, blank=True)
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    created_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='headline_created_pics')  # 紐づくProfileが削除されたらNULL設定
    updated_at = models.DateTimeField('Updated at', auto_now=True)
    updated_pic = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True, related_name='headline_updated_pics')  # 紐づくProfileが削除されたらNULL設定

    def __str__(self):
        return f'<Headline:id={self.id}, {self.name}>'

    def save(self, *args, **kwargs):

        if self.pk:
            orig = self.__class__.objects.filter(pk=self.pk).first()
            if self.images and orig and self.images != orig.images: # djangoのバグ対処　自動保存時でupload_to保存が再帰的に実行される
                self.images = crop_16_9_image(self.images, 1500) # Update the themes size

        super().save(*args, **kwargs)
    