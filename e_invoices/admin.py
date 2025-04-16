from django.contrib import admin
from e_invoices.models import Invoice
from e_invoices.models import Myinvoiceportal
from e_invoices.models import Sapfagll03
from e_invoices.models import Twa0101
from e_invoices.models import Twa0101Item
from e_invoices.models import Ocr
from e_invoices.models import Ocritem
from e_invoices.models import Company
from e_invoices.models import UserProfile
from e_invoices.models import NumberDistribution
from e_invoices.models import TWB2BMainItem
from e_invoices.models import TWB2BLineItem


admin.site.register(Invoice)
admin.site.register(Myinvoiceportal)
admin.site.register(Sapfagll03)
admin.site.register(Twa0101)
admin.site.register(Ocr)
admin.site.register(Ocritem)
admin.site.register(Company)
admin.site.register(UserProfile)
admin.site.register(Twa0101Item)
admin.site.register(NumberDistribution)
admin.site.register(TWB2BMainItem)
admin.site.register(TWB2BLineItem)


# Register your models here.
