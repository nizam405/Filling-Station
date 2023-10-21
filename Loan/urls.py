from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    LoanView, 
    LenderView, LenderUpdateView, 
    BorrowerView, BorrowerUpdateView,
    BorrowLoanCreateView, BorrowLoanUpdateView, BorrowLoanDeleteView,
    RefundBorrowedLoanCreateView, RefundBorrowedLoanUpdateView, RefundBorrowedLoanDeleteView,
    LendLoanCreateView, LendLoanUpdateView, LendLoanDeleteView,
    RefundLendedLoanCreateView, RefundLendedLoanUpdateView, RefundLendedLoanDeleteView,
    )

urlpatterns = [
    path('', LoanView.as_view(), name='loan-dashboard'),
    path('lender/', include([
        path('', LenderView.as_view(), name='lender'),
        path('<int:pk>/', LenderUpdateView.as_view(), name='update-lender'),
    ])),
    
    path('borrower/', include([
        path('', BorrowerView.as_view(), name='borrower'),
        path('<int:pk>/', BorrowerUpdateView.as_view(), name='update-borrower'),
    ])),
    path('borrowed-loan/', include([
        path('new/', BorrowLoanCreateView.as_view(), name='create-borrowed-loan'),
        path('<int:loan_pk>/', include([
            path('update/', BorrowLoanUpdateView.as_view(), name='update-borrowed-loan'),
            path('delete/', BorrowLoanDeleteView.as_view(), name='delete-borrowed-loan'),
            path('refund/', include([
                path('new/', RefundBorrowedLoanCreateView.as_view(), name='create-refund-borrowed-loan'),
                path('<int:pk>/', include([
                    path('update/', RefundBorrowedLoanUpdateView.as_view(), name='update-refund-borrowed-loan'),
                    path('delete/', RefundBorrowedLoanDeleteView.as_view(), name='delete-refund-borrowed-loan'),
                ])),
            ])),
        ])),
    ])),
    
    path('lended-loan/', include([
        path('new/', LendLoanCreateView.as_view(), name='create-lended-loan'),
        path('<int:loan_pk>/', include([
            path('update/', LendLoanUpdateView.as_view(), name='update-lended-loan'),
            path('delete/', LendLoanDeleteView.as_view(), name='delete-lended-loan'),
            path('refund/', include([
                path('new/', RefundLendedLoanCreateView.as_view(), name='create-refund-lended-loan'),
                path('<int:pk>/', include([
                    path('update/', RefundLendedLoanUpdateView.as_view(), name='update-refund-lended-loan'),
                    path('delete/', RefundLendedLoanDeleteView.as_view(), name='delete-refund-lended-loan'),
                ])),
            ])),
        ])),
    ])),
]
