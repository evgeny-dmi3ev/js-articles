# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms

from . import models


class AutoAppConfigFormMixin(object):
    """
    If there is only a single AppConfig to choose, automatically select it.
    """
    def __init__(self, *args, **kwargs):
        super(AutoAppConfigFormMixin, self).__init__(*args, **kwargs)
        if 'app_config' in self.fields:
            # if has only one choice, select it by default
            if self.fields['app_config'].queryset.count() == 1:
                self.fields['app_config'].empty_label = None


class NewsBlogArchivePluginForm(AutoAppConfigFormMixin, forms.ModelForm):
    class Meta:
        model = models.NewsBlogArchivePlugin
        fields = ['app_config', 'cache_duration']


class NewsBlogArticleSearchPluginForm(AutoAppConfigFormMixin, forms.ModelForm):
    class Meta:
        model = models.NewsBlogArticleSearchPlugin
        fields = ['app_config', 'max_articles']


class NewsBlogAuthorsPluginForm(AutoAppConfigFormMixin, forms.ModelForm):
    class Meta:
        model = models.NewsBlogAuthorsPlugin
        fields = ['app_config']


class NewsBlogCategoriesPluginForm(AutoAppConfigFormMixin, forms.ModelForm):
    class Meta:
        model = models.NewsBlogCategoriesPlugin
        fields = ['app_config']


class NewsBlogFeaturedArticlesPluginForm(AutoAppConfigFormMixin,
                                         forms.ModelForm):
    class Meta:
        model = models.NewsBlogFeaturedArticlesPlugin
        fields = ['app_config', 'article_count']


class NewsBlogLatestArticlesPluginForm(AutoAppConfigFormMixin,
                                       forms.ModelForm):
    class Meta:
        model = models.NewsBlogLatestArticlesPlugin
        fields = [
            'app_config', 'latest_articles', 'exclude_featured',
            'cache_duration'
        ]


class NewsBlogTagsPluginForm(AutoAppConfigFormMixin, forms.ModelForm):
    class Meta:
        fields = ['app_config']


class NewsBlogRelatedPluginForm(forms.ModelForm):
    class Meta:
        fields = ['cache_duration']


class NewsBlogJSRelatedPluginForm(forms.ModelForm):
    from django.contrib.admin.widgets import FilteredSelectMultiple

    CHOICES = [
        ('columns', 'Columns'),
        ('rows', 'Rows'),
        ('hero', 'Hero'),
        ('articles', 'Articles'),
    ]
    layout = forms.ChoiceField(CHOICES)

    featured = forms.BooleanField(label='Show "Is Featured"', required=False)

    exclude_current_article = forms.BooleanField(label='Exclude current article', required=False)

    from aldryn_newsblog.models import NewsBlogConfig
    related_types = forms.ModelMultipleChoiceField(
        label='Related sections',
        queryset=NewsBlogConfig.objects.all(),
        required=False,
        widget=FilteredSelectMultiple("Related sections", is_stacked=False))

    from aldryn_people.models import Person
    related_authors = forms.ModelMultipleChoiceField(queryset=Person.objects.all(), required=False, widget=FilteredSelectMultiple("Related authors", is_stacked=False))

    from aldryn_categories.models import Category
    related_categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), required=False, widget=FilteredSelectMultiple("Related categories", is_stacked=False))

    from js_services.models import Service
    related_services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('Related services', False)
    )

    class Meta:
        fields = ['title', 'icon', 'image', 'number_of_articles', 'layout', 'featured', 'exclude_current_article', 'related_types', 'related_authors', 'related_categories']
