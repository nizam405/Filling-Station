from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')
from .views import product, purchase_sell, rate, storage_reading, ledger

urlpatterns = [
    path('', product.ProductView.as_view(), name='products'),
    path('<int:pk>/', include([
        path('update/', product.ProductUpdateView.as_view(), name="update-product"),
        path('delete/', product.ProductDeleteView.as_view(), name="delete-product"),
        path('status/', product.change_product_status, name="change-product-status"),
    ])),

    path('purchase/<date:date>/', include([
        path('create/', purchase_sell.PurchaseCreateView.as_view(), name="create-purchase"),
        path('<int:pk>/update/', purchase_sell.PurchaseUpdateView.as_view(), name="update-purchase"),
        path('<int:pk>/delete/', purchase_sell.PurchaseDeleteView.as_view(), name="delete-purchase"),
    ])),
    path('sell/<date:date>/', include([
        path('create/', purchase_sell.SellCreateView.as_view(), name="create-sell"),
        path('<int:pk>update/', purchase_sell.SellUpdateView.as_view(), name="update-sell"),
        path('<int:pk>delete/', purchase_sell.SellDeleteView.as_view(), name="delete-sell"),
    ])),
    path('rate-variant/', include([
        path('purchase-rate/', include([
            path('create/', rate.PurchaseRateVariantCreateView.as_view(), name='purchase-rate-variant'),
            path('<int:pk>/update/', rate.PurchaseRateVariantUpdateView.as_view(), name='update-purchase-rate-variant'),
            path('<int:pk>/delete/', rate.PurchaseRateVariantDeleteView.as_view(), name='delete-purchase-rate-variant'),
        ])),
        path('selling-rate/', include([
            path('create/', rate.SellingRateVariantCreateView.as_view(), name='selling-rate-variant'),
            path('<int:pk>/update/', rate.SellingRateVariantUpdateView.as_view(), name='update-selling-rate-variant'),
            path('<int:pk>/delete/', rate.SellingRateVariantDeleteView.as_view(), name='delete-selling-rate-variant'),
        ])),
    ])),
    path('<int:product>/', include([
        path('purchase-rate/', include([
            path('create/', rate.PurchaseRateCreateView.as_view(), name='create-purchase-rate'),
            path('<int:pk>/', include([
                path('update/', rate.PurchaseRateUpdateView.as_view(), name='update-purchase-rate'),
                path('delete/', rate.PurchaseRateDeleteView.as_view(), name='delete-purchase-rate'),
            ])),
            path('<int:variant>/', include([
                path('create/', rate.PurchaseRateCreateView.as_view(), name='create-purchase-rate'),
                path('<int:pk>/', include([
                    path('update/', rate.PurchaseRateUpdateView.as_view(), name='update-purchase-rate'),
                    path('delete/', rate.PurchaseRateDeleteView.as_view(), name='delete-purchase-rate'),
                ])),
            ])),
        ])),
        path('selling-rate/', include([
            path('create/', rate.SellingRateCreateView.as_view(), name='create-selling-rate'),
            path('<int:pk>', include([
                path('update/', rate.SellingRateUpdateView.as_view(), name='update-selling-rate'),
                path('delete/', rate.SellingRateDeleteView.as_view(), name='delete-selling-rate'),
            ])),
            path('<int:variant>/',include([
                path('create/', rate.SellingRateCreateView.as_view(), name='create-selling-rate'),
                path('<int:pk>', include([
                    path('update/', rate.SellingRateUpdateView.as_view(), name='update-selling-rate'),
                    path('delete/', rate.SellingRateDeleteView.as_view(), name='delete-selling-rate'),
                ])),
            ])),
        ])),
    ])),
    path('storage/', include([
        path('', storage_reading.StorageReadingView.as_view(), 
            name='daily-product-storage'
        ),
        path('<int:pk>/update/', 
            storage_reading.StorageReadingUpdateView.as_view(), 
            name='update-daily-product-storage'
        ),
        path('<date:date>/', include([
            path('', storage_reading.StorageReadingView.as_view(), 
                name='daily-product-storage'
            ),
            path('<int:pk>/update/', 
                storage_reading.StorageReadingUpdateView.as_view(), 
                name='update-daily-product-storage'
            ),
        ])),
        path('<int:pk>/delete/', storage_reading.StorageReadingDeleteView.as_view(), name='delete-daily-product-storage'),
    ])),
    path('stock-adjustment/<int:stock>/', include([
        path('excesse/', storage_reading.ExcessCreateView.as_view(), name='create-excess'),
        path('excesse/update/<int:pk>/', storage_reading.ExcessUpdateView.as_view(), name='update-excess'),
        path('shortage/', include([
            path('', storage_reading.ShortageCreateView.as_view(), name='create-shortage'),
            path('<int:pk>/', include([
                path('update/', storage_reading.ShortageUpdateView.as_view(), name='update-shortage'),
                path('delete/', storage_reading.ShortageDeleteView.as_view(), name='delete-shortage'),
            ])),
        ])),
    ])),
    # Ledger
    path('product/', include([
        path('topsheet/', include([
            path('', ledger.ProductTopSheet.as_view(), name='product-topsheet'),
            path('<date:date>/', ledger.ProductTopSheet.as_view(), name='product-topsheet'),
        ])),
        path('<int:product>/<date:date>/', ledger.ProductLedger.as_view(), name='product-ledger'),
        # Initial Stock
        path('stock/<date:date>/', include([
            path('', ledger.InitialStockView.as_view(), name='initial-stock'),
            path('create/', ledger.InitialStockCreateView.as_view(), name='create-initial-stock'),
            path('<int:pk>/update/', ledger.InitialStockUpdateView.as_view(), name='update-initial-stock'),
            path('<int:pk>/delete/', ledger.InitialStockDeleteView.as_view(), name='delete-initial-stock'),
        ])),
        path('stock-ledger/', include([
            path('<int:product_id>/', ledger.StockListView.as_view(), name='stock-list'),
            path('<int:pk>/details/', ledger.StockDetailsView.as_view(), name='stock-details'),
        ])),
    ])),
]
