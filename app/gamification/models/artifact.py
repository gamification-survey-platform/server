from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator


class Artifact(models.Model):

    # pdf
    file_extension_validator = FileExtensionValidator(
        allowed_extensions=['pdf'])

    entity = models.ForeignKey('Entity', on_delete=models.CASCADE)

    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE)

    # TO-DO - check if default=now is correct after deployment
    upload_time = models.DateTimeField(
        _('upload time'), null=True, default=now, blank=True)

    file = models.FileField(
        _('assignment file'),
        upload_to='assignment_files',
        blank=True,
        validators=[file_extension_validator],
        help_text=_('Upload a PDF file.'))

    # @property
    # def artifact_reviews(self):
    #     return ArtifactReview.objects.filter(artifact=self)

    # TO-DO - consider about the logic of this function
    # @property
    # def feedback(self):
    #     return Feedback.objects.filter(review_id=ArtifactReview.objects.filter(artifact=self))

    # @property
    # def reviewers(self):
    #     return [artifact_review.user for artifact_review in self.artifact_reviews]

    class Meta:
        db_table = 'artifact'
        verbose_name = _('artifact')
        verbose_name_plural = _('artifacts')
