"""Main public routes: registration, success page."""
import os
import re

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_mail import Message

from app import db, mail
from app.models import Participant
from app.utils import generate_qr_code, generate_registration_id

main_bp = Blueprint('main', __name__)


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def _validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def _validate_phone(phone: str) -> bool:
    pattern = r'^[+]?[\d\s\-()\[\]]{7,20}$'
    return bool(re.match(pattern, phone))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@main_bp.route('/')
def index():
    """Landing page with registration stats."""
    total = Participant.query.count()
    seminars = current_app.config['SEMINARS']
    seminar_stats = [
        {'name': s, 'count': Participant.query.filter_by(seminar=s).count()}
        for s in seminars
    ]
    return render_template('index.html', total=total, seminar_stats=seminar_stats)


@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle participant registration."""
    seminars = current_app.config['SEMINARS']

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        organization = request.form.get('organization', '').strip()
        seminar = request.form.get('seminar', '').strip()

        # --- Server-side validation ---
        errors = []
        if not name or len(name) < 2:
            errors.append('Full name must be at least 2 characters.')
        if not email or not _validate_email(email):
            errors.append('Please enter a valid email address.')
        if not phone or not _validate_phone(phone):
            errors.append('Please enter a valid phone number (7–20 digits).')
        if not organization:
            errors.append('Organization / College is required.')
        if not seminar or seminar not in seminars:
            errors.append('Please select a valid seminar from the list.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('register.html', seminars=seminars,
                                   form_data=request.form)

        # --- Duplicate checks ---
        if Participant.query.filter_by(email=email).first():
            flash('This email address is already registered.', 'warning')
            return render_template('register.html', seminars=seminars,
                                   form_data=request.form)

        if Participant.query.filter_by(phone=phone).first():
            flash('This phone number is already registered.', 'warning')
            return render_template('register.html', seminars=seminars,
                                   form_data=request.form)

        # --- Create record ---
        try:
            reg_id = generate_registration_id()
            qr_text = (f"Registration ID: {reg_id}\n"
                       f"Name: {name}\n"
                       f"Seminar: {seminar}")

            # Persist QR code image
            qr_dir = os.path.join(current_app.static_folder, 'qrcodes')
            os.makedirs(qr_dir, exist_ok=True)
            qr_file = os.path.join(qr_dir, f"{reg_id}.png")
            generate_qr_code(qr_text, save_path=qr_file)

            participant = Participant(
                registration_id=reg_id,
                name=name,
                email=email,
                phone=phone,
                organization=organization,
                seminar=seminar,
                qr_code_path=f"qrcodes/{reg_id}.png",
            )
            db.session.add(participant)
            db.session.commit()

            # Send confirmation email (non-blocking failure)
            try:
                _send_confirmation_email(participant)
            except Exception as exc:
                current_app.logger.warning(f"Email send failed: {exc}")

            return redirect(url_for('main.success', reg_id=reg_id))

        except Exception as exc:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {exc}")
            flash('An unexpected error occurred. Please try again.', 'danger')
            return render_template('register.html', seminars=seminars,
                                   form_data=request.form)

    return render_template('register.html', seminars=seminars, form_data={})


@main_bp.route('/success/<reg_id>')
def success(reg_id: str):
    """Show registration success page with QR code."""
    participant = Participant.query.filter_by(
        registration_id=reg_id).first_or_404()
    qr_text = (f"Registration ID: {participant.registration_id}\n"
               f"Name: {participant.name}\n"
               f"Seminar: {participant.seminar}")
    qr_base64 = generate_qr_code(qr_text)
    return render_template('success.html', participant=participant,
                           qr_code=qr_base64)


# ---------------------------------------------------------------------------
# Email helper
# ---------------------------------------------------------------------------

def _send_confirmation_email(participant: Participant) -> None:
    """Send HTML confirmation email to the newly registered participant."""
    msg = Message(
        subject=f"[Confirmed] {participant.seminar} – Registration {participant.registration_id}",
        recipients=[participant.email],
        html=render_template('email/confirmation.html',
                             participant=participant),
    )
    mail.send(msg)
