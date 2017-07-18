from django.db import models

from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    InlinePanel,
    PageChooserPanel,
    StreamFieldPanel
)

from wagtail.wagtailcore.blocks import (
    TextBlock,
    StructBlock,
    StreamBlock,
    FieldBlock,
    CharBlock,
    RichTextBlock,
    RawHTMLBlock
)

from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.wagtailsearch import index
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from modelcluster.tags import ClusterTaggableManager
from modelcluster.fields import ParentalKey

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from taggit.models import TaggedItemBase

from django import forms

# Create your models here.


class LinkFields(models.Model):
    """LinkFields.

    sometext
    """

    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        """link.

        sometext
        """
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    api_fields = ['link_external', 'link_page', 'link_document']

    class Meta:
        """Meta.

        sometext
        """

        abstract = True


class RelatedLink(LinkFields):
    """RelatedLink.

    sometext
    """

    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    api_fields = ['title'] + LinkFields.api_fields

    class Meta:
        """Meta.

        sometext
        """

        abstract = True


class BlogIndexPage(Page):
    """BlogIndexPage.

    Sometext.
    """

    intro = RichTextField(blank=True)


class BlogIndexPageRelatedLink(Orderable, RelatedLink):
    """BlogIndexPageRelatedLink.

    Sometext
    """

    page = ParentalKey('BlogIndexPage', related_name='related_links')

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
    ]

    api_fields = ['intro', 'related_links']

    @property
    def blogs(self):
        """blogs.

        Get list of live blog pages that are descendants of this page
        """
        blogs = BlogPage.objects.live().descendant_of(self)

        # Order by most recent date first
        blogs = blogs.order_by('-date')

        return blogs

    def get_context(self, request):
        """get_context.

        Get blogs
        """
        blogs = self.blogs

        # Filter by tag
        tag = request.GET.get('tag')
        if tag:
            blogs = blogs.filter(tags__name=tag)

        # Pagination
        page = request.GET.get('page')
        paginator = Paginator(blogs, 10)  # Show 10 blogs per page
        try:
            blogs = paginator.page(page)
        except PageNotAnInteger:
            blogs = paginator.page(1)
        except EmptyPage:
            blogs = paginator.page(paginator.num_pages)

        # Update template context
        context = super(BlogIndexPage, self).get_context(request)
        context['blogs'] = blogs
        return context

BlogIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('intro', classname="full"),
    InlinePanel('related_links', label="Related links"),
]

BlogIndexPage.promote_panels = Page.promote_panels


class CarouselItem(LinkFields):
    """CarouselItem.

    sometext.
    """

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('embed_url'),
        FieldPanel('caption'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    api_fields = ['image', 'embed_url', 'caption'] + LinkFields.api_fields

    class Meta:
        """Meta.

        sometext.
        """

        abstract = True


class BlogPageCarouselItem(Orderable, CarouselItem):
    """BlogPageCarouselItem.

    sometext
    """

    page = ParentalKey('BlogPage', related_name='carousel_items')


class BlogPageRelatedLink(Orderable, RelatedLink):
    """BlogPageRelatedLink.

    sometext
    """

    page = ParentalKey('BlogPage', related_name='related_links')


class BlogPageTag(TaggedItemBase):
    """BlogPageTag.

    sometext
    """

    content_object = ParentalKey('BlogPage', related_name='tagged_items')


class ImageFormatChoiceBlock(FieldBlock):
    """ImageFormatChoiceBlock.

    sometext
    """

    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'),
        ('right', 'Wrap right'),
        ('mid', 'Mid width'),
        ('full', 'Full width'),
    ))


class ImageBlock(StructBlock):
    """ImageBlock.

    Sometext
    """

    image = ImageChooserBlock()
    caption = RichTextBlock()
    alignment = ImageFormatChoiceBlock()


class PullQuoteBlock(StructBlock):
    """PullQuoteBlock.

    sometext.
    """

    quote = TextBlock("quote title")
    attribution = CharBlock()

    class Meta:
        """Meta.

        sometext
        """

        icon = "openquote"


class HTMLAlignmentChoiceBlock(FieldBlock):
    """HTMLAlignmentChoiceBlock.

    Sometext.
    """

    field = forms.ChoiceField(choices=(
        ('normal', 'Normal'),
        ('full', 'Full width'),
    ))


class AlignedHTMLBlock(StructBlock):
    """AlignedHTMLBlock.

    sometext.
    """

    html = RawHTMLBlock()
    alignment = HTMLAlignmentChoiceBlock()

    class Meta:
        """Meta.

        sometext
        """

        icon = "code"


class DemoStreamBlock(StreamBlock):
    """DemoStreamBlock.

    sometext
    """

    h2 = CharBlock(icon="title", classname="title")
    h3 = CharBlock(icon="title", classname="title")
    h4 = CharBlock(icon="title", classname="title")
    intro = RichTextBlock(icon="pilcrow")
    paragraph = RichTextBlock(icon="pilcrow")
    aligned_image = ImageBlock(label="Aligned image", icon="image")
    pullquote = PullQuoteBlock()
    aligned_html = AlignedHTMLBlock(icon="code", label='Raw HTML')
    document = DocumentChooserBlock(icon="doc-full-inverse")


class BlogPage(Page):
    """BlogPage.

    sometext
    """

    body = StreamField(DemoStreamBlock())
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    date = models.DateField("Post date")
    feed_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + [
        index.SearchField('body'),
    ]

    api_fields = ['body', 'tags', 'date', 'feed_image',
                  'carousel_items', 'related_links']

    @property
    def blog_index(self):
        """blog_index.

        Find closest ancestor which is a blog index
        """
        return self.get_ancestors().type(BlogIndexPage).last()

BlogPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('date'),
    StreamFieldPanel('body'),
    InlinePanel('carousel_items', label="Carousel items"),
    InlinePanel('related_links', label="Related links"),
]

BlogPage.promote_panels = Page.promote_panels + [
    ImageChooserPanel('feed_image'),
    FieldPanel('tags'),
]
