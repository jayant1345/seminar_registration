"""Utility functions for the application."""
import base64
import uuid
from datetime import datetime
from io import BytesIO


def generate_registration_id() -> str:
    """Generate a unique registration ID in format SEM-YYYY-XXXXXX."""
    year = datetime.now().year
    unique_part = uuid.uuid4().hex[:6].upper()
    return f"SEM-{year}-{unique_part}"


def generate_qr_code(data: str, save_path: str = None) -> str:
    """
    Generate a QR code for the given data.

    Args:
        data: The string to encode in the QR code.
        save_path: Optional file path to save the QR code image.

    Returns:
        Base64-encoded PNG string for inline HTML display.
    """
    try:
        import qrcode
        from qrcode.image.pil import PilImage

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        if save_path:
            img.save(save_path)

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    except Exception:
        # Return empty string if QR generation fails (e.g., missing library)
        return ''
