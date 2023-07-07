import django_filters

from api_yamdb.reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтрация по полям."""
    category = django_filters.CharFilter(field_name='category__slug')
    genre = django_filters.CharFilter(field_name='genre__slug')
    name = django_filters.CharFilter(
        field_name='name'
    )
    year = django_filters.NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'name', 'year')
