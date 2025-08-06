from django.contrib import admin

class ValorRangeFilter(admin.SimpleListFilter):
    title = 'Faixa de Preço'
    parameter_name = 'valor'

    def lookups(self, request, model_admin):
        return [
            ('0a50', 'Até R$ 50'),
            ('50a100', 'Entre R$ 50 e R$ 100'),
            ('100a150', 'Entre R$ 100 e R$ 150'),
            ('150a200', 'Entre R$ 150 e R$ 200'),
            ('maisde200', 'Acima de R$ 200'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0a50':
            return queryset.filter(valor__lt=50)
        if self.value() == '50a100':
            return queryset.filter(valor__gte=50, valor__lte=100)
        if self.value() == '100a150':
            return queryset.filter(valor__gte=100, valor__lte=150)
        if self.value() == '150a200':
            return queryset.filter(valor__range=(150, 200))
        if self.value() == 'maisde200':
            return queryset.filter(valor__gt=200)
        return queryset
