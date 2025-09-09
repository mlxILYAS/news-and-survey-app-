from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, FormView, CreateView, DeleteView, TemplateView
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import F
import math

from .forms import SurveyResponseForm, ArticleForm, SurveyForm, QuestionFormSet, ProfileUpdateForm
from .models import Article, Survey, Response, ResponseAnswer, Question, QuestionChoice


def is_superuser(user):
	return user.is_superuser


@login_required
def profile(request):
	if request.method == 'POST':
		form = ProfileUpdateForm(request.POST, instance=request.user.profile)
		if form.is_valid():
			form.save()
			messages.success(request, 'Profile updated successfully!')
			return redirect('news:profile')
	else:
		form = ProfileUpdateForm(instance=request.user.profile)
	
	context = {
		'form': form,
		'user': request.user,
		'profile': request.user.profile,
	}
	return render(request, 'registration/profile.html', context)


@user_passes_test(is_superuser)
def user_management(request):
	if request.method == 'POST':
		user_id = request.POST.get('user_id')
		action = request.POST.get('action')
		
		try:
			user = User.objects.get(id=user_id)
			if action == 'make_vip':
				user.profile.is_vip = True
				user.profile.save()
				messages.success(request, f'{user.username} is now VIP!')
			elif action == 'remove_vip':
				user.profile.is_vip = False
				user.profile.save()
				messages.success(request, f'{user.username} VIP status removed!')
			elif action == 'delete_user':
				if user != request.user:  # Prevent self-deletion
					user.delete()
					messages.success(request, f'User {user.username} deleted!')
				else:
					messages.error(request, 'You cannot delete yourself!')
		except User.DoesNotExist:
			messages.error(request, 'User not found!')
		
		return redirect('news:user_management')
	
	# Get all users with their profiles and survey responses
	users = User.objects.select_related('profile').prefetch_related(
		'survey_responses__survey',
		'survey_responses__answers__question'
	).all().order_by('username')
	
	context = {
		'users': users,
	}
	return render(request, 'user_management.html', context)


@user_passes_test(is_superuser)
def survey_results(request):
	# Get all surveys with their responses
	surveys = Survey.objects.prefetch_related(
		'responses__user__profile',
		'responses__answers__question',
		'responses__answers__selected_choices'
	).all()
	
	# Calculate statistics
	total_responses = sum(survey.responses.count() for survey in surveys)
	total_users = User.objects.filter(profile__is_vip=True).count()
	
	context = {
		'surveys': surveys,
		'total_responses': total_responses,
		'total_users': total_users,
	}
	return render(request, 'survey_results.html', context)


class HomeView(ListView):
	model = Article
	template_name = 'home.html'
	context_object_name = 'articles'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['surveys'] = Survey.objects.all()[:5]  # Show latest 5 surveys
		# For guest users, show most visited news
		if not self.request.user.is_authenticated:
			context['most_visited'] = Article.objects.filter(views__gt=0).order_by('-views', '-published_at')[:6]
		else:
			context['most_visited'] = Article.objects.none()
		return context


def user_is_vip(user) -> bool:
	return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_vip


class VipRequiredMixin:
	@method_decorator(login_required(login_url='/login/'))
	def dispatch(self, request: HttpRequest, *args, **kwargs):
		if not user_is_vip(request.user):
			return HttpResponseForbidden('VIP access required.')
		return super().dispatch(request, *args, **kwargs)


class SuperuserRequiredMixin:
	@method_decorator(user_passes_test(is_superuser, login_url='/login/'))
	def dispatch(self, request: HttpRequest, *args, **kwargs):
		return super().dispatch(request, *args, **kwargs)


class ArticleCreateView(CreateView):
	model = Article
	form_class = ArticleForm
	template_name = 'article_create.html'
	success_url = '/'

	def form_valid(self, form):
		# Let the ModelForm handle saving the uploaded image (request.FILES is already bound)
		response = super().form_valid(form)
		messages.success(self.request, 'Article created successfully!')
		return response

	def form_invalid(self, form):
		# Note: Browsers clear file inputs when a form has errors; user will need to reselect the image.
		messages.error(self.request, 'Please correct the errors below.')
		return super().form_invalid(form)


class ArticleDetailView(DetailView):
	model = Article
	template_name = 'article_detail.html'
	slug_url_kwarg = 'slug'
	context_object_name = 'article'

	def get_object(self, queryset=None):
		obj = super().get_object(queryset)
		# Increment views safely to track popularity
		Article.objects.filter(pk=obj.pk).update(views=F('views') + 1)
		obj.refresh_from_db(fields=['views'])
		return obj

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		
		# Parse tags string into a list of chips
		raw_tags = (self.object.tags or "")
		tags_list = [t.strip() for t in raw_tags.replace('#', '').replace(';', ',').split(',') if t.strip()]
		context['tags_list'] = tags_list

		# Reading time estimation (~220 wpm)
		words = len((self.object.content or "").split())
		reading_time = max(1, math.ceil(words / 220)) if words else 1
		context['reading_time'] = reading_time
		context['word_count'] = words
		
		# Get related articles (same author or similar topics)
		context['related_articles'] = Article.objects.filter(
			author=self.object.author
		).exclude(id=self.object.id)[:3]
		return context


class ArticleDeleteView(SuperuserRequiredMixin, DeleteView):
	model = Article
	template_name = 'article_confirm_delete.html'
	slug_url_kwarg = 'slug'
	success_url = '/'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title'] = f"Delete Article: {self.object.title}"
		return context


class SurveyDeleteView(SuperuserRequiredMixin, DeleteView):
	model = Survey
	template_name = 'survey_confirm_delete.html'
	success_url = '/surveys/'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['title'] = f"Delete Survey: {self.object.title}"
		return context


class SuperuserDashboardView(SuperuserRequiredMixin, TemplateView):
	template_name = 'superuser_dashboard.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		# Statistics
		from django.contrib.auth.models import User
		from .models import Article, Survey, Response

		context['total_users'] = User.objects.count()
		context['vip_users'] = User.objects.filter(profile__is_vip=True).count()
		context['total_articles'] = Article.objects.count()
		context['total_surveys'] = Survey.objects.count()
		context['total_responses'] = Response.objects.count()

		# Recent activity
		context['recent_articles'] = Article.objects.order_by('-published_at')[:5]
		context['recent_surveys'] = Survey.objects.order_by('-created_at')[:5]
		context['recent_responses'] = Response.objects.select_related('user', 'survey').order_by('-submitted_at')[:10]

		# System health
		context['active_surveys'] = Survey.objects.filter(active=True).count()
		context['inactive_surveys'] = Survey.objects.filter(active=False).count()

		return context


class SurveyCreateView(SuperuserRequiredMixin, CreateView):
	model = Survey
	form_class = SurveyForm
	template_name = 'survey_create.html'
	success_url = '/surveys/'

	def form_valid(self, form):
		response = super().form_valid(form)
		messages.success(self.request, 'Survey created successfully! Now add questions.')
		return response


@user_passes_test(is_superuser)
def survey_edit(request, pk):
	"""Edit survey questions and choices"""
	survey = get_object_or_404(Survey, pk=pk)
	
	if request.method == 'POST':
		action = request.POST.get('action')
		
		if action == 'add_question':
			question_text = request.POST.get('question_text')
			question_type = request.POST.get('question_type')
			points = request.POST.get('points', 1)
			correct_answer = request.POST.get('correct_answer', '')
			
			if question_text:
				question = Question.objects.create(
					survey=survey,
					text=question_text,
					question_type=question_type,
					points=points,
					correct_answer=correct_answer,
					order=survey.questions.count() + 1
				)
				messages.success(request, 'Question added successfully!')
				return redirect('news:survey_edit', pk=pk)
		
		elif action == 'add_choice':
			question_id = request.POST.get('question_id')
			choice_text = request.POST.get('choice_text')
			is_correct = request.POST.get('is_correct') == 'on'
			
			if question_id and choice_text:
				question = get_object_or_404(Question, id=question_id, survey=survey)
				QuestionChoice.objects.create(
					question=question,
					text=choice_text,
					is_correct=is_correct,
					order=question.choices.count() + 1
				)
				messages.success(request, 'Choice added successfully!')
				return redirect('news:survey_edit', pk=pk)
		
		elif action == 'delete_question':
			question_id = request.POST.get('question_id')
			if question_id:
				question = get_object_or_404(Question, id=question_id, survey=survey)
				question.delete()
				messages.success(request, 'Question deleted successfully!')
				return redirect('news:survey_edit', pk=pk)
		
		elif action == 'delete_choice':
			choice_id = request.POST.get('choice_id')
			if choice_id:
				choice = get_object_or_404(QuestionChoice, id=choice_id)
				choice.delete()
				messages.success(request, 'Choice deleted successfully!')
				return redirect('news:survey_edit', pk=pk)
	
	context = {
		'survey': survey,
		'questions': survey.questions.all(),
	}
	return render(request, 'survey_edit.html', context)


class SurveyListView(VipRequiredMixin, ListView):
	model = Survey
	template_name = 'survey_list.html'
	context_object_name = 'surveys'


class SurveyDetailView(VipRequiredMixin, FormView, DetailView):
	model = Survey
	template_name = 'survey_detail.html'
	form_class = SurveyResponseForm

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['survey'] = self.get_object()
		return kwargs

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['survey'] = self.get_object()
		return context

	def form_valid(self, form):
		survey = self.get_object()
		user = self.request.user
		response, created = Response.objects.get_or_create(survey=survey, user=user)
		response.answers.all().delete()
		for question in survey.questions.all():
			answer_text = form.cleaned_data.get(f'question_{question.id}', '')
			ResponseAnswer.objects.create(response=response, question=question, answer_text=answer_text)
		# Calculate and save score
		response.calculate_score()
		return redirect(reverse('news:survey_submitted', kwargs={'pk': survey.pk}))


class SurveySubmittedView(VipRequiredMixin, DetailView):
	model = Survey
	template_name = 'survey_submitted.html'
	context_object_name = 'survey'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user = self.request.user
		try:
			response = Response.objects.get(survey=self.object, user=user)
			context['response'] = response
			context['score'] = response.score
			context['max_score'] = response.max_possible_score
		except Response.DoesNotExist:
			context['response'] = None
		return context