import hmac
import hashlib
import base64
import uuid
import requests
from django.conf import settings


# ── Shared ──────────────────────────────────────────────────────────────────

def generate_transaction_uuid():
    return str(uuid.uuid4())


# ── Khalti ──────────────────────────────────────────────────────────────────

def khalti_initiate(order, return_url, website_url):
    """Call Khalti API to get a hosted payment URL. Returns (pidx, payment_url) or raises."""
    # Khalti works in paisa (1 NPR = 100 paisa). Using total as NPR for demo.
    amount_paisa = int(float(order.total) * 100)

    payload = {
        'return_url': return_url,
        'website_url': website_url,
        'amount': amount_paisa,
        'purchase_order_id': str(order.id),
        'purchase_order_name': f'GreatStore Order #{order.id}',
        'customer_info': {
            'name': order.full_name,
            'email': order.email,
            'phone': order.phone or '9800000000',
        },
    }
    headers = {'Authorization': f'Key {settings.KHALTI_SECRET_KEY}'}
    resp = requests.post(settings.KHALTI_INITIATE_URL, json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    return data.get('pidx'), data.get('payment_url')


def khalti_verify(pidx):
    """Verify a Khalti payment by pidx. Returns the response dict."""
    headers = {'Authorization': f'Key {settings.KHALTI_SECRET_KEY}'}
    resp = requests.post(settings.KHALTI_VERIFY_URL, json={'pidx': pidx}, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ── eSewa ───────────────────────────────────────────────────────────────────

def esewa_signature(message: str) -> str:
    """Generate HMAC-SHA256 base64 signature for eSewa v2."""
    key = settings.ESEWA_SECRET_KEY.encode('utf-8')
    msg = message.encode('utf-8')
    return base64.b64encode(hmac.new(key, msg, hashlib.sha256).digest()).decode('utf-8')


def esewa_form_data(order, transaction_uuid, success_url, failure_url):
    """Build all POST fields required by eSewa v2 payment form."""
    total_amount = str(order.total)
    product_code = settings.ESEWA_MERCHANT_CODE
    signed_fields = 'total_amount,transaction_uuid,product_code'
    message = f'total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}'

    return {
        'amount': str(order.total),
        'tax_amount': '0',
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
        'product_code': product_code,
        'product_service_charge': '0',
        'product_delivery_charge': '0',
        'success_url': success_url,
        'failure_url': failure_url,
        'signed_field_names': signed_fields,
        'signature': esewa_signature(message),
    }


def esewa_verify(product_code, total_amount, transaction_uuid):
    """Check eSewa payment status via their status API."""
    params = {
        'product_code': product_code,
        'total_amount': total_amount,
        'transaction_uuid': transaction_uuid,
    }
    resp = requests.get(settings.ESEWA_VERIFY_URL, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()
