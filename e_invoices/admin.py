from django.contrib import admin
#from e_invoices.models import Invoice
#from e_invoices.models import Myinvoiceportal
#from e_invoices.models import Sapfagll03
from e_invoices.models import Twa0101
from e_invoices.models import Twa0101Item
from e_invoices.models import Ocr
from e_invoices.models import Ocritem
from e_invoices.models import Company
from e_invoices.models import UserProfile
from e_invoices.models import NumberDistribution
from e_invoices.models import TWB2BMainItem
from e_invoices.models import TWB2BLineItem
from e_invoices.models import TWAllowance
from e_invoices.models import TWAllowanceLineItem
from e_invoices.models import CompanyNotificationConfig
from e_invoices.models import SystemConfig
from e_invoices.models import Buyer
from e_invoices.models import TWB2BMainItemInS
from e_invoices.models import TWB2BLineItemInS
from e_invoices.models import TWB2BMainItemInE
from e_invoices.models import TWB2BLineItemInE


from django.contrib.admin.widgets import RelatedFieldWidgetWrapper


class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'company_id', 'company_name', 'company_identifier',
        'company_type', 'head_company_identifer', 'is_foreign_ecomm'
    )
    search_fields = ('company_id', 'company_name')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "head_company_identifer":
            kwargs["limit_choices_to"] = {'company_type': 0}
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)

            # 用 RelatedFieldWidgetWrapper 並手動關掉按鈕
            widget = RelatedFieldWidgetWrapper(
                formfield.widget,
                db_field.remote_field,
                self.admin_site,
                can_add_related=False,
                can_change_related=False,
                can_delete_related=False,
            )
            formfield.widget = widget
            return formfield

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
#admin.site.register(Invoice)
#admin.site.register(Myinvoiceportal)
#admin.site.register(Sapfagll03)
#admin.site.register(Twa0101)
admin.site.register(Ocr)
admin.site.register(Ocritem)
admin.site.register(Company, CompanyAdmin)
admin.site.register(UserProfile)
#admin.site.register(Twa0101Item)
admin.site.register(NumberDistribution)
admin.site.register(TWB2BMainItem)
admin.site.register(TWB2BLineItem)
admin.site.register(TWAllowance)
admin.site.register(TWAllowanceLineItem)
admin.site.register(CompanyNotificationConfig)
admin.site.register(SystemConfig)
admin.site.register(TWB2BMainItemInE)
admin.site.register(TWB2BMainItemInS)
admin.site.register(TWB2BLineItemInE)
admin.site.register(TWB2BLineItemInS)
admin.site.register(Buyer)




# Register your models here.
