from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Q, Sum

from .models import (Lender, Borrower, BorrowLoan, RefundBorrowedLoan, LendLoan, RefundLendedLoan)
from Transaction.functions import last_balance_date, get_next_month, get_current_month 
from Transaction.models import CashBalance
from Core.mixins import RedirectMixin
    

# হাওলাদ দাতা
class LenderView(RedirectMixin, CreateView, ListView):
    model = Lender
    fields = '__all__'
    template_name = 'Loan/lender.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

class LenderUpdateView(RedirectMixin, UpdateView, ListView):
    model = Lender
    fields = '__all__'
    template_name = 'Loan/lender.html'
    success_url = reverse_lazy('lender')

# হাওলাদ গ্রহীতা
class BorrowerView(RedirectMixin, CreateView, ListView):
    model = Borrower
    fields = '__all__'
    template_name = 'Loan/borrower.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

class BorrowerUpdateView(RedirectMixin, UpdateView, ListView):
    model = Borrower
    fields = '__all__'
    template_name = 'Loan/borrower.html'
    success_url = reverse_lazy('borrower')

# হাওলাদ (ড্যাসবোর্ড)
class LoanView(RedirectMixin, TemplateView):
    template_name = "Loan/loan_dashboard.html"  

    def get(self, request, *args, **kwargs):
        if not CashBalance.objects.exists():
            return redirect("daily-transactions")
        return super().get(request, *args, **kwargs)  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_month = get_current_month()
        next_month = get_next_month()

        # হাওলাদ গ্রহণ (চলতি মাস ও চলতি লেনদেন)
        borrowed_loans = BorrowLoan.objects.filter(
            Q(is_finished=False) |
            (
                Q(refunds__date__gte=current_month) &
                Q(refunds__date__lt=next_month) &
                Q(is_finished=True)
            )
        ).distinct()
        if borrowed_loans:
            result_set = []
            total_borrowed_loan_refund = 0
            for loan in borrowed_loans.order_by("-date"):
                refunds = RefundBorrowedLoan.objects.filter(loan=loan)
                total_borrowed_loan_refund += refunds.aggregate(Sum('amount'))['amount__sum'] or 0
                loan_dict = {'loan':loan,'refunds':refunds}
                result_set.append(loan_dict)

            context['borrowed_loans'] = result_set
            total_borrowed_loan = borrowed_loans.aggregate(Sum('amount'))['amount__sum']
            context['total_borrowed_loan'] = total_borrowed_loan
            context['total_borrowed_loan_refund'] = total_borrowed_loan_refund
            context['total_borrowed_loan_remaining'] = total_borrowed_loan - total_borrowed_loan_refund
        
        # হাওলাদ প্রদান (চলতি মাস ও চলতি লেনদেন)
        lended_loans = LendLoan.objects.filter(
            Q(is_finished=False) |
            (
                Q(refunds__date__gte=current_month) &
                Q(refunds__date__lt=next_month) &
                Q(is_finished=True)
            )
        ).distinct()
        if lended_loans:
            result_set = []
            total_lended_loan_refund = 0
            for loan in lended_loans.order_by("-date"):
                refunds = RefundLendedLoan.objects.filter(loan=loan)
                total_lended_loan_refund += refunds.aggregate(Sum('amount'))['amount__sum'] or 0
                loan_dict = {'loan':loan,'refunds':refunds}
                result_set.append(loan_dict)

            context['lended_loans'] = result_set
            total_lended_loan = lended_loans.aggregate(Sum('amount'))['amount__sum']
            context['total_lended_loan'] = total_lended_loan
            context['total_lended_loan_refund'] = total_lended_loan_refund
            context['total_lended_loan_remaining'] = total_lended_loan - total_lended_loan_refund

            context['lended_loans'] = result_set

        return context

class BorrowedLoanDetailView(RedirectMixin, TemplateView):
    model = Lender
    loan_model = BorrowLoan
    refund_model = RefundBorrowedLoan
    template_name = "Loan/borrowed_loan_details.html" 

    def get(self, request, *args, **kwargs):
        if not CashBalance.objects.exists():
            return redirect("daily-transactions")
        return super().get(request, *args, **kwargs) 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lender = self.model.objects.get(pk=self.kwargs['pk'])
        context['lender'] = lender
        loans = self.loan_model.objects.filter(lender=lender)
        if loans:
            result_set = []
            total_loan_refund = 0
            for loan in loans.order_by("-date"):
                refunds = self.refund_model.objects.filter(loan=loan)
                total_loan_refund += refunds.aggregate(Sum('amount'))['amount__sum'] or 0
                loan_dict = {'loan':loan,'refunds':refunds}
                result_set.append(loan_dict)

            context['loans'] = result_set
            total_loan = loans.aggregate(Sum('amount'))['amount__sum']
            context['total_loan'] = total_loan
            context['total_loan_refund'] = total_loan_refund
            context['total_loan_remaining'] = total_loan - total_loan_refund
        
        return context  

class LendedLoanDetailView(RedirectMixin, TemplateView):
    model = Borrower
    loan_model = LendLoan
    refund_model = RefundLendedLoan
    template_name = "Loan/lended_loan_details.html" 

    def get(self, request, *args, **kwargs):
        if not CashBalance.objects.exists():
            return redirect("daily-transactions")
        return super().get(request, *args, **kwargs) 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        borrower = self.model.objects.get(pk=self.kwargs['pk'])
        context['borrower'] = borrower
        loans = self.loan_model.objects.filter(borrower=borrower)
        if loans:
            result_set = []
            total_loan_refund = 0
            for loan in loans.order_by("-date"):
                refunds = self.refund_model.objects.filter(loan=loan)
                total_loan_refund += refunds.aggregate(Sum('amount'))['amount__sum'] or 0
                loan_dict = {'loan':loan,'refunds':refunds}
                result_set.append(loan_dict)

            context['loans'] = result_set
            total_loan = loans.aggregate(Sum('amount'))['amount__sum']
            context['total_loan'] = total_loan
            context['total_loan_refund'] = total_loan_refund
            context['total_loan_remaining'] = total_loan - total_loan_refund
        
        return context  

# হাওলাদ গ্রহণ
class BorrowLoanCreateView(RedirectMixin, CreateView):
    model = BorrowLoan
    template_name = "Loan/loan_form.html"
    fields = ['date','lender','amount']
    success_url = reverse_lazy('loan-dashboard')

    def get(self, request, *args, **kwargs):
        if not CashBalance.objects.exists():
            return redirect("daily-transactions")
        return super().get(request, *args, **kwargs) 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "হাওলাদ গ্রহণ"
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        initial['date'] = last_balance_date()
        return initial
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].disabled = True  # Disable the date field
        return form

class BorrowLoanUpdateView(RedirectMixin, UpdateView):
    model = BorrowLoan
    template_name = "Loan/loan_form.html"
    fields = ['date','lender','amount']
    success_url = reverse_lazy('loan-dashboard')

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs['loan_pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "হাওলাদ গ্রহণ (পরিবর্তন)"
        return context
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].disabled = True  # Disable the date field
        return form

class BorrowLoanDeleteView(RedirectMixin, DeleteView):
    model = BorrowLoan
    template_name = "Loan/loan_confirm_delete.html"
    success_url = reverse_lazy('loan-dashboard')

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs['loan_pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'হাওলাদ গ্রহণ - বাতিল'
        return context

class RefundBorrowedLoanCreateView(RedirectMixin, CreateView):
    model = RefundBorrowedLoan
    template_name = "Loan/refund_loan_form.html"
    fields = ['date','loan','amount']
    success_url = reverse_lazy('loan-dashboard')

    def get_initial(self):
        initial = super().get_initial()
        loan = BorrowLoan.objects.get(pk=self.kwargs['loan_pk'])
        initial['loan'] = loan
        initial['date'] = last_balance_date()
        return initial
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].disabled = True  # Disable the date field
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "গৃহীত হাওলাদ পরিশোধ"
        return context

class RefundBorrowedLoanUpdateView(RedirectMixin, UpdateView):
    model = RefundBorrowedLoan
    template_name = "Loan/refund_loan_form.html"
    fields = ['date','loan','amount']
    success_url = reverse_lazy('loan-dashboard')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].disabled = True  # Disable the date field
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "গৃহীত হাওলাদ পরিশোধ (পরিবর্তন)"
        return context

class RefundBorrowedLoanDeleteView(RedirectMixin, DeleteView):
    model = RefundBorrowedLoan
    success_url = reverse_lazy('loan-dashboard')

#  হাওলাদ প্রদান
class LendLoanCreateView(RedirectMixin, CreateView):
    model = LendLoan
    template_name = "Loan/loan_form.html"
    fields = ['date','borrower','amount']
    success_url = reverse_lazy('loan-dashboard')

    def get(self, request, *args, **kwargs):
        if not CashBalance.objects.exists():
            return redirect("daily-transactions")
        return super().get(request, *args, **kwargs) 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "হাওলাদ প্রদান"
        return context
    
    def get_initial(self):
        initial = super().get_initial()
        initial['date'] = last_balance_date()
        return initial
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].disabled = True  # Disable the date field
        return form

class LendLoanUpdateView(RedirectMixin, UpdateView):
    model = LendLoan
    template_name = "Loan/loan_form.html"
    fields = ['date','borrower','amount']
    success_url = reverse_lazy('loan-dashboard')

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs['loan_pk'])
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].disabled = True  # Disable the date field
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "হাওলাদ প্রদান (পরিবর্তন)"
        return context

class LendLoanDeleteView(RedirectMixin, DeleteView):
    model = LendLoan
    template_name = "Loan/loan_confirm_delete.html"
    success_url = reverse_lazy('loan-dashboard')

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs['loan_pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'হাওলাদ প্রদান - বাতিল'
        return context

class RefundLendedLoanCreateView(RedirectMixin, CreateView):
    model = RefundLendedLoan
    template_name = "Loan/refund_loan_form.html"
    fields = ['date','loan','amount']
    success_url = reverse_lazy('loan-dashboard')

    def get_initial(self):
        initial = super().get_initial()
        loan = LendLoan.objects.get(pk=self.kwargs['loan_pk'])
        initial['loan'] = loan
        initial['date'] = last_balance_date()
        return initial
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].disabled = True  # Disable the date field
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "প্রদত্ত হাওলাদ ফেরত"
        return context

class RefundLendedLoanUpdateView(RedirectMixin, UpdateView):
    model = RefundLendedLoan
    template_name = "Loan/refund_loan_form.html"
    fields = ['date','loan','amount']
    success_url = reverse_lazy('loan-dashboard')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].disabled = True  # Disable the date field
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "প্রদত্ত হাওলাদ ফেরত (পরিবর্তন)"
        return context

class RefundLendedLoanDeleteView(RedirectMixin, DeleteView):
    model = RefundLendedLoan
    success_url = reverse_lazy('loan-dashboard')
