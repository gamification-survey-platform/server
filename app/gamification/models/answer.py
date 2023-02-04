from django.db import models

class Answer(models.Model):
    """
    Model for Answer
    """
    artifact_review = models.ForeignKey('ArtifactReview', on_delete=models.CASCADE)

    #registration = models.ForeignKey('Registration', on_delete=models.CASCADE)

    question_option = models.ForeignKey('QuestionOption', on_delete=models.CASCADE)

    answer_text = models.TextField(blank=True)

    class Meta:
        db_table = 'answer'
        verbose_name = 'answer'
        verbose_name_plural = 'answers'

class ArtifactFeedback(Answer):
    page = models.CharField(('page'), max_length=150, blank=True)
    class Meta():
        db_table = 'artifact_feedback'
        verbose_name = ('artifact_feedback')
        verbose_name_plural = ('artifact_feedback')
