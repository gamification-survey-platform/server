from django.db import models
from django.utils.translation import gettext_lazy as _


class ArtifactReview(models.Model):
    class ArtifactReviewType(models.TextChoices):
        COMPLETED = "COMPLETED"
        INCOMPLETE = "INCOMPLETE"
        REOPEN = "REOPEN"
        OPTIONAL_INCOMPLETE = "OPTIONAL_INCOMPLETE"
        LATE = "LATE"

    artifact = models.ForeignKey("Artifact", on_delete=models.CASCADE)

    user = models.ForeignKey("Registration", on_delete=models.CASCADE)

    status = models.TextField(choices=ArtifactReviewType.choices, default=ArtifactReviewType.INCOMPLETE)

    artifact_review_score = models.IntegerField(default=None, null=True, blank=True)

    max_artifact_review_score = models.IntegerField(default=None, null=True, blank=True)

    class Meta:
        db_table = "artifact_review"
        verbose_name = _("artifact_review")
        verbose_name_plural = _("artifact_reviews")
