from django.conf import settings
from django.db import models


VISIBILITY_CHOICES = [
    ("private", "Private"),
    ("unlisted", "Unlisted"),
    ("public", "Public"),
]


class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    symbol = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "currencies"
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code


class TransactionKind(models.Model):
    # user=None means "global/built-in kind"
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transaction_kinds",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=50)

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="private",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transaction_kinds"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["user", "name"]),
            models.Index(fields=["visibility"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="uniq_transaction_kind_per_owner",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class FinanceCategory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="finance_categories",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#007AFF")
    icon = models.CharField(max_length=50, blank=True, null=True)

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="private",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "finance_categories"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["user", "name"]),
            models.Index(fields=["visibility"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="uniq_finance_category_per_owner",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class PaymentMethod(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_methods",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="private",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_methods"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["user", "name"]),
            models.Index(fields=["visibility"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="uniq_payment_method_per_owner",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class Merchant(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="merchants",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="private",
    )
    is_active = models.BooleanField(default=True)

    # Optional: requires locations app with Place model.
    place = models.ForeignKey(
        "locations.Place",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="merchants",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "merchants"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["user", "name"]),
            models.Index(fields=["visibility"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="uniq_merchant_per_owner",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class FinanceTag(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="finance_tags",
    )
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "finance_tags"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="uniq_finance_tag_per_user"),
        ]
        indexes = [
            models.Index(fields=["user", "name"]),
        ]

    def __str__(self) -> str:
        return self.name


class Budget(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    category = models.ForeignKey(
        FinanceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="budgets",
    )

    # Store budgets per month; use first day of month, e.g. 2026-03-01
    month = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)

    currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="budgets",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "budgets"
        ordering = ["-month"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "category", "month", "currency"],
                name="uniq_budget_user_category_month_currency",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "month"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} budget {self.month} - {self.amount}"


class Transaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    kind = models.ForeignKey(
        TransactionKind,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    amount_currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions_amount",
    )

    # Optional base amounts (for normalized reporting)
    base_amount = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    base_currency = models.ForeignKey(
        Currency,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions_base",
    )
    exchange_rate = models.DecimalField(max_digits=18, decimal_places=8, blank=True, null=True)

    occurred_at = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    merchant = models.ForeignKey(
        Merchant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    # Optional: requires locations.Place
    place = models.ForeignKey(
        "locations.Place",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )

    tags = models.ManyToManyField(
        FinanceTag,
        blank=True,
        related_name="transactions",
    )

    metadata = models.JSONField(blank=True, null=True)

    inferred = models.BooleanField(default=False)
    confidence = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transactions"
        ordering = ["-occurred_at"]
        indexes = [
            models.Index(fields=["user", "occurred_at"]),
            models.Index(fields=["merchant", "occurred_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} {self.amount} @ {self.occurred_at}"


class TransactionSplit(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name="splits",
    )
    category = models.ForeignKey(
        FinanceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transaction_splits",
    )

    amount = models.DecimalField(max_digits=14, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "transaction_splits"
        indexes = [
            models.Index(fields=["transaction"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self) -> str:
        return f"Split {self.amount} ({self.transaction_id})"