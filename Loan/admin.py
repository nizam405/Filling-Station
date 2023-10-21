from django.contrib import admin
from .models import Lender, BorrowLoan, Borrower, LendLoan, RefundBorrowedLoan, RefundLendedLoan

admin.site.register(Lender)
admin.site.register(BorrowLoan)
admin.site.register(RefundBorrowedLoan)

admin.site.register(Borrower)
admin.site.register(LendLoan)
admin.site.register(RefundLendedLoan)