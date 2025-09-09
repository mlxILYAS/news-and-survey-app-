from django.contrib import admin

from .models import Article, Profile, Survey, Question, Response, ResponseAnswer


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'published_at')
	search_fields = ('title', 'author')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'is_vip')
	list_filter = ('is_vip',)
	search_fields = ('user__username',)


class QuestionInline(admin.TabularInline):
	model = Question
	extra = 1


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
	list_display = ('title', 'created_at')
	inlines = [QuestionInline]


class ResponseAnswerInline(admin.TabularInline):
	model = ResponseAnswer
	extra = 0


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
	list_display = ('survey', 'user', 'submitted_at')
	inlines = [ResponseAnswerInline] 