from django.db import models

class Customer(models.Model):
    ntn_cnic = models.CharField(max_length=15, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    name = models.CharField(max_length=255)
    province = models.CharField(max_length=30, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    registration_type = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.name

    def select(self):
        return {
            'id': self.id,
            'name': self.name,
        }

class Item(models.Model):
    hs_code = models.CharField(max_length=15, null=True, blank=True)
    description = models.CharField(max_length=255)
    uo_m = models.CharField(max_length=30, null=True, blank=True)
    purchase_rate = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    sale_rate = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.description
    
    def select(self):
        return {
            'id': self.id,
            'name': self.description
        }

class Invoice(models.Model):
    invoice_type = models.CharField(max_length=50)
    invoice_date = models.DateField()
    invoice_number = models.CharField(max_length=50)
    invoice_number_fbr = models.CharField(max_length=50, null=True, blank=True)
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.CASCADE)
    invoice_ref_no = models.CharField(max_length=50, null=True, blank=True)
    scenario_id = models.CharField(max_length=50, null=True, blank=True)

    
    def __str__(self):
        return self.invoice_number

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', null=True, blank=True, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rate = models.CharField(max_length=10, null=True, blank=True)
    uo_m = models.CharField(max_length=30, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    total_values = models.DecimalField(max_digits=14, decimal_places=0, null=True, blank=True)
    value_sales_excluding_st = models.DecimalField(max_digits=14, decimal_places=0, null=True, blank=True)
    fixed_notified_value_or_retail_price = models.DecimalField(max_digits=14, decimal_places=0, null=True, blank=True)
    sales_tax_applicable = models.DecimalField(max_digits=14, decimal_places=0, null=True, blank=True)
    sales_tax_withheld_at_source = models.DecimalField(max_digits=14, decimal_places=0, null=True, blank=True)
    extra_tax = models.DecimalField(max_digits=14, decimal_places=0, null=True, blank=True)
    further_tax = models.DecimalField(max_digits=14, decimal_places=0, null=True, blank=True)
    sro_schedule_no = models.CharField(max_length=50, null=True, blank=True)
    fed_payable = models.DecimalField(max_digits=14, decimal_places=0, null=True, blank=True)
    discount = models.DecimalField(max_digits=14, decimal_places=0, null=True, blank=True)
    sale_type = models.CharField(max_length=100)
    sro_item_serial_no = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.invoice.invoice_number

    def select(self):
        return {
            'name': self.item.description,
            'quantity': float(self.quantity)
        }

