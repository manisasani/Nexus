param([string]$command)

switch ($command) {
    "up" {
        docker compose up
    }

    "down" {
        docker compose down
    }

    "build" {
        docker compose up --build
    }

    "migrate" {
        docker compose exec web python manage.py migrate
    }

    "makemigrations" {
        docker compose exec web python manage.py makemigrations
    }

    "superuser" {
        docker compose exec web python manage.py createsuperuser
    }

    "logs" {
        docker compose logs -f web
    }

    "shell" {
        docker compose exec web python manage.py shell
    }

    "bash" {
        docker compose exec web sh
    }

    default {
        Write-Host "Available commands:"
        Write-Host "up"
        Write-Host "down"
        Write-Host "build"
        Write-Host "migrate"
        Write-Host "makemigrations"
        Write-Host "superuser"
        Write-Host "logs"
        Write-Host "shell"
        Write-Host "bash"
    }
}

"celery-logs" { docker compose logs -f celery_worker }
"celery-shell" { docker compose exec celery_worker sh }