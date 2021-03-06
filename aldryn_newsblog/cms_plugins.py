# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime

from distutils.version import LooseVersion
from django.utils.translation import ugettext_lazy as _

from cms import __version__ as cms_version
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from . import models, forms
from .utils import add_prefix_to_path, default_reverse

CMS_GTE_330 = LooseVersion(cms_version) >= LooseVersion('3.3.0')


class TemplatePrefixMixin(object):

    def get_render_template(self, context, instance, placeholder):
        if (hasattr(instance, 'app_config') and
                instance.app_config.template_prefix):
            return add_prefix_to_path(
                self.render_template,
                instance.app_config.template_prefix
            )
        return self.render_template


class NewsBlogPlugin(TemplatePrefixMixin, CMSPluginBase):
    module = 'JumpSuite Articles'


class AdjustableCacheMixin(object):
    """
    For django CMS < 3.3.0 installations, we have no choice but to disable the
    cache where there is time-sensitive information. However, in later CMS
    versions, we can configure it with `get_cache_expiration()`.
    """
    if not CMS_GTE_330:
        cache = False

    def get_cache_expiration(self, request, instance, placeholder):
        return getattr(instance, 'cache_duration', 0)

    def get_fieldsets(self, request, obj=None):
        """
        Removes the cache_duration field from the displayed form if we're not
        using django CMS v3.3.0 or later.
        """
        fieldsets = super(AdjustableCacheMixin, self).get_fieldsets(request, obj=None)
        if CMS_GTE_330:
            return fieldsets

        field = 'cache_duration'
        for fieldset in fieldsets:
            new_fieldset = [
                item for item in fieldset[1]['fields'] if item != field]
            fieldset[1]['fields'] = tuple(new_fieldset)
        return fieldsets


@plugin_pool.register_plugin
class NewsBlogArchivePlugin(AdjustableCacheMixin, NewsBlogPlugin):
    render_template = 'aldryn_newsblog/plugins/archive.html'
    name = _('Archive')
    model = models.NewsBlogArchivePlugin
    form = forms.NewsBlogArchivePluginForm

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance

        queryset = models.Article.objects

        context['dates'] = queryset.get_months(
            request,
            namespace=instance.app_config.namespace
        )
        return context


@plugin_pool.register_plugin
class NewsBlogArticleSearchPlugin(NewsBlogPlugin):
    render_template = 'aldryn_newsblog/plugins/article_search.html'
    name = _('Article Search')
    model = models.NewsBlogArticleSearchPlugin
    form = forms.NewsBlogArticleSearchPluginForm

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        context['query_url'] = default_reverse('{0}:article-search'.format(
            instance.app_config.namespace), default=None)
        return context


@plugin_pool.register_plugin
class NewsBlogAuthorsPlugin(NewsBlogPlugin):
    render_template = 'aldryn_newsblog/plugins/authors.html'
    name = _('Authors')
    model = models.NewsBlogAuthorsPlugin
    form = forms.NewsBlogAuthorsPluginForm

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        context['authors_list'] = instance.get_authors(request)
        context['article_list_url'] = default_reverse(
            '{0}:article-list'.format(instance.app_config.namespace),
            default=None)

        return context


@plugin_pool.register_plugin
class NewsBlogCategoriesPlugin(NewsBlogPlugin):
    render_template = 'aldryn_newsblog/plugins/categories.html'
    name = _('Categories')
    model = models.NewsBlogCategoriesPlugin
    form = forms.NewsBlogCategoriesPluginForm
    cache = False

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        context['categories'] = instance.get_categories(request)
        context['article_list_url'] = default_reverse(
            '{0}:article-list'.format(instance.app_config.namespace),
            default=None)
        return context


@plugin_pool.register_plugin
class NewsBlogFeaturedArticlesPlugin(NewsBlogPlugin):
    render_template = 'aldryn_newsblog/plugins/featured_articles.html'
    name = _('Featured Articles')
    model = models.NewsBlogFeaturedArticlesPlugin
    form = forms.NewsBlogFeaturedArticlesPluginForm

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        context['articles_list'] = instance.get_articles(request)
        return context


@plugin_pool.register_plugin
class NewsBlogLatestArticlesPlugin(AdjustableCacheMixin, NewsBlogPlugin):
    render_template = 'aldryn_newsblog/plugins/latest_articles.html'
    name = _('Latest Articles')
    model = models.NewsBlogLatestArticlesPlugin
    form = forms.NewsBlogLatestArticlesPluginForm

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        context['article_list'] = instance.get_articles(request)
        return context


@plugin_pool.register_plugin
class NewsBlogRelatedPlugin(AdjustableCacheMixin, NewsBlogPlugin):
    render_template = 'aldryn_newsblog/plugins/related_articles.html'
    name = _('Specific Articles')
    model = models.NewsBlogRelatedPlugin
    form = forms.NewsBlogRelatedPluginForm

    def get_article(self, request):
        if request and request.resolver_match:
            view_name = request.resolver_match.view_name
            namespace = request.resolver_match.namespace
            if view_name == '{0}:article-detail'.format(namespace):
                article = models.Article.objects.active_translations(
                    slug=request.resolver_match.kwargs['slug'])
                if article.count() == 1:
                    return article[0]
        return None

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        article = self.get_article(request)
        if article:
            context['article'] = article
            context['article_list'] = instance.get_articles(article, request)
        return context


@plugin_pool.register_plugin
class NewsBlogJSRelatedPlugin(AdjustableCacheMixin, NewsBlogPlugin):
    # render_template = 'aldryn_newsblog/plugins/js_related_articles.html'
    name = _('Related Articles')
    model = models.NewsBlogJSRelatedPlugin
    form = forms.NewsBlogJSRelatedPluginForm
    # change_form_template = "aldryn_newsblog/plugins/js_related_articles_admin.html"

    def get_article(self, request):
        if request and request.resolver_match:
            view_name = request.resolver_match.view_name
            namespace = request.resolver_match.namespace
            if view_name == '{0}:article-detail'.format(namespace):
                article = models.Article.objects.active_translations(
                    slug=request.resolver_match.kwargs['slug'])
                if article.count() == 1:
                    return article[0]
        return None

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance

        context['title'] = instance.title
        context['icon'] = instance.icon
        context['image'] = instance.image
        layout = instance.layout
        featured = instance.featured
        exclude_current_article = instance.exclude_current_article
        related_types = instance.related_types
        related_authors = instance.related_authors.all()
        related_categories = instance.related_categories.all()
        related_services = instance.related_services.all()

        qs = models.Article.objects.all().filter(is_published=True).filter(publishing_date__lte=datetime.datetime.now()).distinct()
        if related_types.exists():
            qs = qs.filter(app_config__in=related_types.all())
        if related_authors:
            qs = qs.filter(author__in=related_authors.all())
        if related_categories:
            qs = qs.filter(categories__in=related_categories.all())
        if related_services:
            qs = qs.filter(services__in=related_services.all())
        if exclude_current_article:
            current_article = self.get_article(request)
            if current_article is not None:
                qs = qs.exclude(id=current_article.id)
        if featured:
            qs = qs.filter(is_featured=True)
        related_articles = qs[:int(instance.number_of_articles)]

        context['related_articles'] = related_articles

        related_types_first = instance.related_types.first()
        if related_types_first is not None:
            context['related_types_first'] = related_types_first.namespace
        else:
            context['related_types_first'] = 'all'
        related_categories_first = instance.related_categories.all().first()
        if related_categories_first is not None:
            context['related_categories_first'] = related_categories_first.slug
        else:
            context['related_categories_first'] = 'all'
        related_authors_first = instance.related_authors.all().first()
        if related_authors_first is not None:
            context['related_authors_first'] = related_authors_first.slug

        if layout == 'columns':
            self.render_template = 'aldryn_newsblog/plugins/js_related_articles__cols.html'
        elif layout == 'rows':
            self.render_template = 'aldryn_newsblog/plugins/js_related_articles__rows.html'
        elif layout == 'hero':
            self.render_template = 'aldryn_newsblog/plugins/js_related_articles__hero.html'
        elif layout == 'articles':
            self.render_template = 'aldryn_newsblog/plugins/js_related_articles__articles.html'

        return context


@plugin_pool.register_plugin
class NewsBlogTagsPlugin(NewsBlogPlugin):
    render_template = 'aldryn_newsblog/plugins/tags.html'
    name = _('Tags')
    model = models.NewsBlogTagsPlugin
    form = forms.NewsBlogTagsPluginForm

    def render(self, context, instance, placeholder):
        request = context.get('request')
        context['instance'] = instance
        context['tags'] = instance.get_tags(request)
        context['article_list_url'] = default_reverse(
            '{0}:article-list'.format(instance.app_config.namespace),
            default=None)
        return context
