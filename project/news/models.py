from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Article(models.Model):
	title = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255, unique=True, blank=True)
	content = models.TextField()
	author = models.CharField(max_length=255)
	category = models.CharField(max_length=100, default='General')
	tags = models.CharField(max_length=255, blank=True, default='')
	image = models.ImageField(upload_to='articles/', blank=True, null=True)
	published_at = models.DateTimeField(default=timezone.now)
	excerpt = models.TextField(max_length=300, blank=True)
	views = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ['-published_at']

	def save(self, *args, **kwargs):
		# Generate a unique slug based on the title
		if not self.slug:
			base_slug = slugify(self.title)
			slug = base_slug or 'article'
			counter = 1
			# Ensure uniqueness (avoid IntegrityError on duplicate titles)
			while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
				slug = f"{base_slug}-{counter}"
				counter += 1
			self.slug = slug

		# Auto-generate excerpt if not provided
		if not self.excerpt:
			self.excerpt = self.content[:300] + '...' if len(self.content) > 300 else self.content

		super().save(*args, **kwargs)

	def __str__(self) -> str:
		return self.title


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	is_vip = models.BooleanField(default=False)

	def __str__(self) -> str:
		status = 'VIP' if self.is_vip else 'Normal'
		return f"{self.user.username} ({status})"


class Survey(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	active = models.BooleanField(default=True)
	max_slots = models.PositiveIntegerField(default=10, help_text="Maximum number of VIP users who can answer")
	slot_duration_hours = models.PositiveIntegerField(default=24, help_text="How long each slot is valid (in hours)")
	
	def available_slots(self):
		"""Calculate how many slots are still available"""
		used_slots = self.responses.count()
		return max(0, self.max_slots - used_slots)
	
	def has_available_slot(self):
		"""Check if there are any available slots"""
		return self.available_slots() > 0
	
	def __str__(self):
		return self.title


class Question(models.Model):
	TEXT = 'text'
	MULTIPLE_CHOICE = 'multiple_choice'
	RADIO = 'radio'
	CHECKBOX = 'checkbox'
	
	QUESTION_TYPES = [
		(TEXT, 'Text Answer'),
		(MULTIPLE_CHOICE, 'Multiple Choice'),
		(RADIO, 'Single Choice'),
		(CHECKBOX, 'Multiple Selection'),
	]
	
	survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
	text = models.CharField(max_length=500)
	question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default=TEXT)
	order = models.PositiveIntegerField(default=0)
	required = models.BooleanField(default=True)
	points = models.PositiveIntegerField(default=1, help_text="Points for correct answer")
	correct_answer = models.TextField(blank=True, help_text="Correct answer for scoring")
	created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
	
	class Meta:
		ordering = ['order']
	
	def __str__(self):
		return f"{self.survey.title} - Q{self.order}: {self.text[:50]}"


class QuestionChoice(models.Model):
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
	text = models.CharField(max_length=200)
	order = models.PositiveIntegerField(default=0)
	is_correct = models.BooleanField(default=False, help_text="Is this the correct answer?")
	
	class Meta:
		ordering = ['order']
	
	def __str__(self):
		return f"{self.question.text[:30]} - {self.text}"


class Response(models.Model):
	survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='survey_responses')
	submitted_at = models.DateTimeField(auto_now_add=True)
	score = models.PositiveIntegerField(default=0, help_text="Total points earned")
	max_possible_score = models.PositiveIntegerField(default=0, help_text="Maximum possible score")
	slot_number = models.PositiveIntegerField(default=1, help_text="Which slot number this response used")
	
	class Meta:
		unique_together = ['survey', 'user']  # One response per user per survey
		ordering = ['-submitted_at']
	
	def calculate_score(self):
		"""Calculate the score based on correct answers"""
		total_score = 0
		max_score = 0
		
		for answer in self.answers.all():
			question = answer.question
			max_score += question.points
			
			if question.question_type == 'text':
				# For text questions, check if answer matches correct_answer
				if answer.answer_text.strip().lower() == question.correct_answer.strip().lower():
					total_score += question.points
			else:
				# For choice questions, check selected choices
				correct_choices = question.choices.filter(is_correct=True)
				selected_choices = answer.selected_choices.all()
				
				if correct_choices.count() == selected_choices.count():
					all_correct = all(choice in correct_choices for choice in selected_choices)
					if all_correct:
						total_score += question.points
		
		self.score = total_score
		self.max_possible_score = max_score
		self.save()
		return total_score
	
	def __str__(self):
		return f"{self.user.username} - {self.survey.title} (Slot {self.slot_number})"


class ResponseAnswer(models.Model):
	response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
	question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
	answer_text = models.TextField(blank=True)
	selected_choices = models.ManyToManyField(QuestionChoice, blank=True)

	def __str__(self) -> str:
		if self.selected_choices.exists():
			choices = ', '.join([choice.text for choice in self.selected_choices.all()])
			return f"{self.question.text[:30]}... -> {choices}"
		return f"{self.question.text[:30]}... -> {self.answer_text[:30]}..." 