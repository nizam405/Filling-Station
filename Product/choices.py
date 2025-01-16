
# Product Categories
PRODUCT_CATEGORIES = [
    ('fuel','জ্বালানী'),
    ('loose_lubricant','লুব্রিকেন্ট (লুস)'),
    ('lubricant','লুব্রিকেন্ট'),
    ('others','অন্যান্য'),
]
FUEL            = PRODUCT_CATEGORIES[0][0]
LOOSE_LUBRICANT = PRODUCT_CATEGORIES[1][0]
LUBRICANT       = PRODUCT_CATEGORIES[2][0]
OTHER_PRODUCT   = PRODUCT_CATEGORIES[3][0]

# Units
# UNIT_CHOICES = [
#     ('piece','পিছ'),
#     ('barrel','ব্যারেল'),
#     ('litre','লিটার'),
#     ('ml','মিঃলিঃ'),
#     ('kg','কেজি'),
#     ('gm','গ্রাম'),
# ]

# Packaging Types
# PACKAGING_TYPES = [
#     ('loose', 'লুস'),
#     ('pack', 'প্যাকেজড'),
# ]
# LOOSE   = PACKAGING_TYPES[0][0]
# PACK    = PACKAGING_TYPES[1][0]

# Stock In type
STOCK_IN_TYPE_CHOICES = [
    ('initial_stock','প্রারম্ভিক মজুদ (হিসাব শুরুর তারিখের)'),
    ('purchase','ক্রয়'),
    # ('excess','উদ্বৃত্ত মাল'),
]
INITIAL_STOCK   = STOCK_IN_TYPE_CHOICES[0][0]
PURCHASE        = STOCK_IN_TYPE_CHOICES[1][0]
# EXCESS = STOCK_IN_TYPE_CHOICES[2][0]

# ConsumeStock type
# CONSUME_CHOICES = [
#     ('sell','বিক্রয়'),
#     ('shortage','ঘাটতি')
# ]
# SELL = CONSUME_CHOICES[0][0]
# SHORTAGE = CONSUME_CHOICES[1][0]
