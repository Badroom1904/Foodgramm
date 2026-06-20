# Foodgram — продуктовый помощник

[![Foodgram CI/CD](https://github.com/Badroom1904/Foodgramm/actions/workflows/main.yml/badge.svg)](https://github.com/Badroom1904/Foodgramm/actions/workflows/main.yml)

**Foodgram** — это веб-приложение, где пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и формировать список покупок из выбранных блюд.

Проект реализован в рамках учебного курса по бэкенд-разработке на Django.

---

## 🌐 Ссылка на проект

Проект доступен по адресу:  
🔗 https://Food.freedynamicdns.org/

---

## 👤 Автор

- **Алексей Маношин**  
- Email: [dreznov1904@gmail.com](mailto:dreznov1904@gmail.com)  
- GitHub: [Badroom1904](https://github.com/Badroom1904)

---

## 🛠 Технологии

**Бэкенд:**
- Python 3.12
- Django 5.2
- Django REST Framework
- Djoser (аутентификация)
- PostgreSQL
- Gunicorn

**Фронтенд:**
- React
- JavaScript
- CSS

**Инфраструктура:**
- Docker
- Docker Compose
- Nginx
- GitHub Actions (CI/CD)
- Docker Hub

---

## 🚀 Как развернуть проект

### С использованием Docker (рекомендуемый способ)

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Badroom1904/Foodgramm.git
   cd Foodgramm

2. Создайте файл .env в папке backend/ со следующим содержимым:
   SECRET_KEY=ваш_секретный_ключ
   DEBUG=False
   ALLOWED_HOSTS=ваш-IP-или-домен
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=ваш_пароль
   DB_HOST=db
   DB_PORT=5432

3.Запустите проект:
   cd infra
   docker-compose up -d

4.Выполните миграции и загрузите ингредиенты:
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py load_ingredients --format csv
   docker-compose exec backend python manage.py createsuperuser