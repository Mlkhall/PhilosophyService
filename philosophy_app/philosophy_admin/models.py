import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class DemoCyberleninka(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cyberleninka_id = models.CharField(max_length=456)
    title = models.CharField(_("Название"), max_length=400)
    authors = models.CharField(_("Авторы"), max_length=400)
    publication_year = models.IntegerField(_("Год публикации"))
    science_magazine_name = models.CharField(_("Название научного журнала"), max_length=400)
    science_magazine_url = models.URLField(_("Ссылка на научный журнал"), max_length=500)
    annotation = models.TextField(_("Аннотация"))
    annotation_en = models.TextField(_("Аннотация en"))
    article_text = models.TextField(_("Текст статьи"))
    field_of_sciences = models.CharField(_("Область науки"), max_length=600)
    tags = models.TextField(_("Теги"))
    keywords = models.TextField(_("Ключевые слова"))
    similar_topics = models.TextField(_("Похожие темы"))
    source_url = models.URLField(_("Ссылка на статью"), max_length=500)
    pdf_url = models.URLField(_("Ссылка на pdf"), max_length=500)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Демоверсия КиберЛенинка")
        verbose_name_plural = _("Демоверсия КиберЛенинка")

        db_table = "demo_cyberleninka"
        constraints = [
            models.UniqueConstraint(fields=["cyberleninka_id"], name="cyberleninka_id_pkey"),
        ]
