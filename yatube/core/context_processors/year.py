from django.utils import timezone


def year(request):
    current_year = timezone.now()
    return {
        'year': current_year.year
    }
