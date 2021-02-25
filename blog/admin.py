from django.contrib import admin
from . import models

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin import AdminSite

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    pass


class PostTitleFilter(admin.SimpleListFilter):
    title = '本文'
    parameter_name = 'body_contains'

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(body__icontains=self.value())
        return queryset

    def lookups(self, request, model_admin):
        return [
            ("ブログ", "「ブログ」を含む"),
            ("日記", "「日記」を含む"),
            ("開発", "「開発」を含む"),
        ]


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'tags_summary', 'published', 'created', 'updated')
    # N+1問題解消(ForeinKey)
    list_select_related = ('category', )
    # 編集可能にする
    list_editable = ('title', 'category')
    # 検索可能にする(ForeinKeyやManyToManyは要素も指定する。)
    search_fields = ('title', 'category__name', 'tags__name', 'created', 'updated')
    # デフォルトの並び順を変更する。
    ordering = ('-updated', '-created')
    # フィルタ機能を追加する。
    list_filter = (PostTitleFilter,'category', 'tags', 'created', 'updated')
    
    # ManyToMany Field 表示
    def tags_summary(self, obj):
        qs = obj.tags.all()
        label = ', '.join(map(str, qs))
        return label
    
    tags_summary.short_description = "tags"
    
    # N+1問題解消(ManyToMany)
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')
        
    # モデルを一括で変更する独自のアクションを追加する。
    actions = ["publish", "unpublish"]

    def publish(self, request, queryset):
        queryset.update(published=True)
        
    publish.short_description = "公開する"
        
    def unpublish(self, request, queryset):
        queryset.update(published=False)
        
    unpublish.short_description = "下書きに戻す"



class BlogAdminSite(AdminSite):
    site_header = 'マイページ'
    site_title = 'マイページ'
    index_title = 'ホーム'
    site_url = None
    login_form = AuthenticationForm

    def has_permission(self, request):
        return request.user.is_active


mypage_site = BlogAdminSite(name="mypage")

mypage_site.register(models.Post)
mypage_site.register(models.Tag)
mypage_site.register(models.Category)
