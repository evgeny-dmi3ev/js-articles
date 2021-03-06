# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from aldryn_apphooks_config.admin import BaseAppHookConfig, ModelAppHookConfig
from aldryn_people.models import Person
from aldryn_translation_tools.admin import AllTranslationsMixin
from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from django.contrib import admin
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from parler.admin import TranslatableAdmin
from parler.forms import TranslatableModelForm
from sortedm2m_filter_horizontal_widget.forms import SortedFilteredSelectMultiple


from . import models

from .constants import (
    HIDE_RELATED_ARTICLES,
    HIDE_TAGS,
    HIDE_USER,
    SUMMARY_RICHTEXT,
)

from cms.admin.placeholderadmin import PlaceholderAdminMixin


def make_published(modeladmin, request, queryset):
    queryset.update(is_published=True)


make_published.short_description = _(
    "Mark selected articles as published")


def make_unpublished(modeladmin, request, queryset):
    queryset.update(is_published=False)


make_unpublished.short_description = _(
    "Mark selected articles as not published")


def make_featured(modeladmin, request, queryset):
    queryset.update(is_featured=True)


make_featured.short_description = _(
    "Mark selected articles as featured")


def make_not_featured(modeladmin, request, queryset):
    queryset.update(is_featured=False)


make_not_featured.short_description = _(
    "Mark selected articles as not featured")


class ArticleAdminForm(TranslatableModelForm):

    class Meta:
        model = models.Article
        fields = [
            'app_config',
            'categories',
            'companies',
            'featured_image',
            'is_featured',
            'is_published',
            'lead_in',
            'meta_description',
            'meta_keywords',
            'meta_title',
            'owner',
            'related',
            'services',
            'slug',
            'tags',
            'title',
        ]

    def __init__(self, *args, **kwargs):
        if 'initial' in kwargs:
            kwargs['initial']['medium'] = models.ArticleMedium.objects.first().pk if models.ArticleMedium.objects.first() else None
        super(ArticleAdminForm, self).__init__(*args, **kwargs)

        qs = models.Article.objects
        if self.instance.app_config_id:
            qs = models.Article.objects.filter(
                app_config=self.instance.app_config)
        elif 'initial' in kwargs and 'app_config' in kwargs['initial']:
            qs = models.Article.objects.filter(
                app_config=kwargs['initial']['app_config'])

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if 'related' in self.fields:
            self.fields['related'].queryset = qs

        # Don't allow app_configs to be added here. The correct way to add an
        # apphook-config is to create an apphook on a cms Page.
        self.fields['app_config'].widget.can_add_related = False
        # Don't allow related articles to be added here.
        # doesn't makes much sense to add articles from another article other
        # than save and add another.
        if ('related' in self.fields and
                hasattr(self.fields['related'], 'widget')):
            self.fields['related'].widget.can_add_related = False
        if not SUMMARY_RICHTEXT:
            self.fields['lead_in'].widget = widgets.Textarea()


class ArticleAdmin(
    PlaceholderAdminMixin,
    FrontendEditableAdminMixin,
    ModelAppHookConfig,
    TranslatableAdmin
):
    form = ArticleAdminForm
    list_display = ('title_view', 'app_config', 'is_featured',
                    'is_published', 'publishing_date')
    list_filter = [
        'app_config',
        'categories',
        'services',
        'companies',
    ]
    actions = (
        make_featured, make_not_featured,
        make_published, make_unpublished,
    )

    def title_view(self, obj):
         return obj.title
    title_view.short_description  = 'title'
    title_view.admin_order_field = 'translations__title'

    advanced_settings_fields = (
        'categories',
        'services',
        'companies',
    )

    if HIDE_TAGS == 0:
        advanced_settings_fields += (
            'tags',
        )

    if HIDE_RELATED_ARTICLES == 0:
        advanced_settings_fields += (
            'related',
        )

    if HIDE_USER == 0:
        advanced_settings_fields += (
            'owner',
        )

    advanced_settings_fields += (
        'app_config',
    )

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'author',
                'author_2',
                'author_3',
                'publishing_date',
                'is_published',
                'is_featured',
                'featured_image',
                'lead_in',
                'medium',
            )
        }),
        (_('Meta Options'), {
            'classes': ('collapse',),
            'fields': (
                'slug',
                'meta_title',
                'meta_description',
                'meta_keywords',
            )
        }),
        (_('Advanced Settings'), {
            'classes': ('collapse',),
            'fields': advanced_settings_fields
        }),
    )



    filter_horizontal = [
        'categories',
    ]
    app_config_values = {
        'default_published': 'is_published'
    }
    app_config_selection_title = ''
    app_config_selection_desc = ''

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'services':
            kwargs['widget'] = SortedFilteredSelectMultiple()
        if db_field.name == 'companies':
            kwargs['widget'] = SortedFilteredSelectMultiple()
        return super(ArticleAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


admin.site.register(models.Article, ArticleAdmin)


class NewsBlogConfigAdmin(
    PlaceholderAdminMixin,
    BaseAppHookConfig,
    TranslatableAdmin
):
    def get_config_fields(self):
        return (
            'app_title', 'permalink_type', 'non_permalink_handling',
            'template_prefix', 'paginate_by', 'pagination_pages_start',
            'pagination_pages_visible', 'exclude_featured',
            'create_authors', 'search_indexed', 'config.default_published',
        )


admin.site.register(models.NewsBlogConfig, NewsBlogConfigAdmin)

admin.site.register(models.ArticleMedium)
