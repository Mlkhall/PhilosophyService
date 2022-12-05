from django.contrib import admin
from django.db import models
from django.forms import Textarea, TextInput
from django.utils.safestring import mark_safe

from .models import DemoCyberleninka


@admin.register(DemoCyberleninka)
class ProductsAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "authors",
        "publication_year",
        "science_magazine_name",
        "science_magazine_url",
        "field_of_sciences",
        "tags",
        "keywords",
        "source_url",
        "pdf_url",
    )
    search_fields = (
        "title",
        "authors",
        "annotation",
        "annotation_en",
        "article_text",
        "tags",
        "keywords",
        "similar_topics",
    )
    list_filter = ("publication_year",)

    formfield_overrides = {
        models.CharField: {"widget": TextInput(attrs={"size": "100"})},
        models.TextField: {"widget": Textarea(attrs={"rows": 10, "cols": 100})},
    }
