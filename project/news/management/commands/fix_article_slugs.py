from django.core.management.base import BaseCommand
from news.models import Article
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Fix article slugs for existing articles'

    def handle(self, *args, **options):
        articles = Article.objects.filter(slug__isnull=True) | Article.objects.filter(slug='')
        
        if not articles:
            self.stdout.write(self.style.SUCCESS('All articles already have slugs!'))
            return
        
        self.stdout.write(f'Found {articles.count()} articles without slugs. Fixing...')
        
        for article in articles:
            # Generate slug from title
            base_slug = slugify(article.title)
            slug = base_slug
            
            # Handle duplicate slugs
            counter = 1
            while Article.objects.filter(slug=slug).exclude(id=article.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            article.slug = slug
            article.save()
            
            self.stdout.write(f'Fixed: "{article.title}" -> slug: "{slug}"')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully fixed {articles.count()} article slugs!')) 