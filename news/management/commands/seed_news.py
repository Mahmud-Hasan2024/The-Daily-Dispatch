from django.core.management.base import BaseCommand
from users.forms import User
from news.models import Category, Article
from faker import Faker
import random
import requests
from django.core.files.base import ContentFile

fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with fake categories and articles (with images)"

    def add_arguments(self, parser):
        parser.add_argument('--categories', type=int, default=5, help='Number of categories')
        parser.add_argument('--articles', type=int, default=20, help='Number of articles')

    def handle(self, *args, **options):
        categories_count = options['categories']
        articles_count = options['articles']

        # Ensure a user exists
        if not User.objects.exists():
            user = User.objects.create_user(username="admin", password="admin123")
            self.stdout.write(self.style.SUCCESS("✅ Created default user: admin / admin123"))
        else:
            user = User.objects.first()

        # Create categories
        categories = []
        for _ in range(categories_count):
            category = Category.objects.create(
                name=fake.word().capitalize(),
                description=fake.sentence()
            )
            categories.append(category)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {categories_count} categories"))

        # Create articles with random images
        for _ in range(articles_count):
            article = Article.objects.create(
                title=fake.sentence(nb_words=6),
                content=fake.paragraph(nb_sentences=15),
                author=user,
                category=random.choice(categories),
                is_published=True
            )

            # Fetch a random image from picsum.photos
            try:
                img_url = f"https://picsum.photos/800/600?random={random.randint(1, 1000)}"
                response = requests.get(img_url)
                if response.status_code == 200:
                    article.image.save(
                        f"article_{article.id}.jpg",
                        ContentFile(response.content),
                        save=True
                    )
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ Could not fetch image: {e}"))

        self.stdout.write(self.style.SUCCESS(f"✅ Created {articles_count} articles with images"))
        self.stdout.write(self.style.SUCCESS("🎉 Database seeded successfully!"))
