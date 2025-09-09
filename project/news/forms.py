from django import forms
from .models import Survey, Question, Article, Profile, QuestionChoice


class ProfileUpdateForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['is_vip']
		widgets = {
			'is_vip': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
		}


class SurveyForm(forms.ModelForm):
	class Meta:
		model = Survey
		fields = ['title', 'description', 'max_slots', 'slot_duration_hours']
		widgets = {
			'title': forms.TextInput(attrs={'class': 'form-control'}),
			'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
			'max_slots': forms.NumberInput(attrs={'class': 'form-control'}),
			'slot_duration_hours': forms.NumberInput(attrs={'class': 'form-control'}),
		}


class QuestionForm(forms.ModelForm):
	class Meta:
		model = Question
		fields = ['text', 'question_type', 'order', 'required', 'points', 'correct_answer']
		widgets = {
			'text': forms.TextInput(attrs={'class': 'form-control'}),
			'question_type': forms.Select(attrs={'class': 'form-control'}),
			'order': forms.NumberInput(attrs={'class': 'form-control'}),
			'required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
			'points': forms.NumberInput(attrs={'class': 'form-control'}),
			'correct_answer': forms.TextInput(attrs={'class': 'form-control'}),
		}


class QuestionChoiceForm(forms.ModelForm):
	class Meta:
		model = QuestionChoice
		fields = ['text', 'order', 'is_correct']
		widgets = {
			'text': forms.TextInput(attrs={'class': 'form-control'}),
			'order': forms.NumberInput(attrs={'class': 'form-control'}),
			'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
		}


class SurveyResponseForm(forms.Form):
	def __init__(self, *args, **kwargs):
		survey: Survey = kwargs.pop('survey')
		super().__init__(*args, **kwargs)
		for question in survey.questions.all():
			field_name = f"question_{question.id}"
			if question.question_type == 'text':
				self.fields[field_name] = forms.CharField(
					label=question.text,
					required=question.required,
					widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
				)
			elif question.question_type == 'radio':
				choices = [(choice.id, choice.text) for choice in question.choices.all()]
				self.fields[field_name] = forms.ChoiceField(
					label=question.text,
					required=question.required,
					choices=choices,
					widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
				)
			elif question.question_type == 'checkbox':
				choices = [(choice.id, choice.text) for choice in question.choices.all()]
				self.fields[field_name] = forms.MultipleChoiceField(
					label=question.text,
					required=question.required,
					choices=choices,
					widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
				)


class ArticleForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Make optional fields explicitly optional with sensible defaults
		if 'category' in self.fields:
			self.fields['category'].required = False
			self.fields['category'].initial = 'General'
		if 'tags' in self.fields:
			self.fields['tags'].required = False
			self.fields['tags'].initial = ''

	class Meta:
		model = Article
		fields = ['title', 'content', 'author', 'category', 'tags', 'image', 'excerpt']
		widgets = {
			'title': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
			'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'required': 'required'}),
			'author': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
			'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Technology, News, Sports'}),
			'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated tags, e.g., tech, ai, python'}),
			'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
			'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief summary of the article (optional)'}),
		}


QuestionFormSet = forms.inlineformset_factory(
	Survey, Question, form=QuestionForm, extra=3, can_delete=True
) 