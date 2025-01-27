from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Link, SentNumber
from . import db
import json
import pywhatkit as kit
from datetime import datetime
import time
from werkzeug.utils import secure_filename
import os

views = Blueprint('views', __name__)

# Add this function to handle profile picture uploads
def save_profile_picture(file):
    if not file:
        return None
    filename = secure_filename(file.filename)
    # Create profiles directory if it doesn't exist
    profile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app/static/profiles')
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
    file_path = os.path.join(profile_path, filename)
    file.save(file_path)
    return filename

@views.route('/')
def home():
    return render_template("home.html", user=current_user)

@views.route('/dashboard')
@login_required
def dashboard():
    links = Link.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", user=current_user, links=links)

@views.route('/add-link', methods=['GET', 'POST'])
@login_required
def add_link():
    if request.method == 'POST':
        url = request.form.get('url')
        description = request.form.get('description')

        if len(url) < 1:
            flash('URL is too short!', category='error')
        else:
            new_link = Link(url=url, description=description, user_id=current_user.id)
            db.session.add(new_link)
            db.session.commit()
            flash('Link added!', category='success')
            return redirect(url_for('views.dashboard'))

    return render_template("add_link.html", user=current_user)

@views.route('/send-message/<int:link_id>', methods=['GET', 'POST'])
@login_required
def send_message(link_id):
    link = Link.query.get_or_404(link_id)
    if link.user_id != current_user.id:
        return redirect(url_for('views.dashboard'))

    if request.method == 'POST':
        platform = request.form.get('platform', 'whatsapp')
        numbers = request.form.get('numbers').split(',')
        message = f"{link.description}\n{link.url}"
        
        success_count = 0
        error_count = 0
        
        for number in numbers:
            number = number.strip()
            if len(number) >= 1:  
                try:
                    if platform == 'whatsapp':
                        if len(number) >= 10:
                            # Get current time
                            now = datetime.now()
                            # Add 2 minutes to current time
                            send_time = now.hour
                            send_minute = now.minute + 2
                            
                            # Send message using pywhatkit
                            kit.sendwhatmsg(number, message, send_time, send_minute)
                            success_count += 1
                        else:
                            error_count += 1
                            flash(f'Invalid WhatsApp number: {number}', category='error')
                            continue
                    else:  # telegram
                        error_count += 1
                        flash(f'Error sending to Telegram {number}: Telegram service is not available', category='error')
                        continue
                    
                    # Record the sent number
                    sent_number = SentNumber(phone_number=number, link_id=link.id, platform=platform)
                    db.session.add(sent_number)
                    
                except Exception as e:
                    error_count += 1
                    flash(f'Error sending to {number}: {str(e)}', category='error')
            else:
                error_count += 1
                flash(f'Invalid number/username: {number}', category='error')
        
        db.session.commit()
        
        if success_count > 0:
            flash(f'Successfully sent message to {success_count} recipient(s)!', category='success')
        if error_count > 0:
            flash(f'Failed to send message to {error_count} recipient(s).', category='error')
                
        return redirect(url_for('views.dashboard'))

    return render_template("send_message.html", user=current_user, link=link)

@views.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@views.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form.get('name')
        bio = request.form.get('bio')
        profile_picture = request.files.get('profile_picture')

        if name:
            current_user.name = name
        if bio:
            current_user.bio = bio
        if profile_picture and profile_picture.filename:
            filename = save_profile_picture(profile_picture)
            if filename:
                current_user.profile_picture = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('views.profile'))

    return render_template('edit_profile.html', user=current_user)
