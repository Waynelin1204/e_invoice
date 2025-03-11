from django.contrib import admin
from e_invoices.models import Invoice
from e_invoices.models import Myinvoiceportal
from e_invoices.models import Sapfagll03
from e_invoices.models import Twa0101
from e_invoices.models import Ocr
from e_invoices.models import Ocritem

admin.site.register(Invoice)
admin.site.register(Myinvoiceportal)
admin.site.register(Sapfagll03)
admin.site.register(Twa0101)
admin.site.register(Ocr)
admin.site.register(Ocritem)


# Register your models here.
