from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import uuid

app = Flask(__name__)
app.config.from_object('config.Config')
db = SQLAlchemy(app)

agent_locations = {
    'ratib.nsamba': 'HQ - Kampala',
    'agent1': 'Branch A',
    'agent2': 'Branch B',
}


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(50))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class DeviceType(db.Model):
    __tablename__ = 'tbl_device_types'
    id = db.Column(db.Integer, primary_key=True)
    device_type = db.Column(db.String(50), nullable=False)


class Category(db.Model):
    __tablename__ = 'tbl_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Institution(db.Model):
    __tablename__ = 'tbl_institutions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)


class Issue(db.Model):
    __tablename__ = 'tbl_device_issues_and_repairs'
    issue_ticket_no = db.Column(db.String(50), primary_key=True)
    diff_in_days = db.Column(db.SmallInteger, nullable=False)
    conformance_to_sla = db.Column(db.String(50))
    terminal_id = db.Column(db.String(50), nullable=False)
    agent_name = db.Column(db.String(50), nullable=False)
    log_date = db.Column(db.DateTime, nullable=False)
    categoryname = db.Column(db.String(50), nullable=False)
    issuedescription = db.Column(db.String(100), nullable=False)
    last_updated_on = db.Column(db.DateTime, nullable=False)
    sla = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    institutionalid = db.Column(db.String(100), nullable=False)
    createdbyname = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)


def generate_ticket_number():
    return 'ISSUE-' + datetime.utcnow().strftime('%Y%m%d') + '-' + uuid.uuid4().hex[:8].upper()


# Ensure database tables exist before requests are handled.
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not username or not password or not confirm:
            flash('Please fill required fields', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return render_template('register.html')

        if email and User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('register.html')

        user = User(username=username, first_name=first_name, last_name=last_name, email=email, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password', 'danger')
        return render_template('login.html')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    summary = {
        'device_types': DeviceType.query.count(),
        'categories': Category.query.count(),
        'institutions': Institution.query.count(),
        'issues': Issue.query.count(),
    }
    latest_issues = Issue.query.order_by(Issue.log_date.desc()).limit(5).all()
    return render_template('dashboard.html', summary=summary, latest_issues=latest_issues)


@app.route('/device-types')
def device_types():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    types = DeviceType.query.order_by(DeviceType.id).all()
    return render_template('device_types.html', types=types)


@app.route('/device-types/new', methods=['GET', 'POST'])
def new_device_type():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('device_type', '').strip()
        if not name:
            flash('Device type is required.', 'danger')
            return render_template('device_type_form.html')

        device_type = DeviceType(device_type=name)
        db.session.add(device_type)
        db.session.commit()
        flash('Device type created.', 'success')
        return redirect(url_for('device_types'))

    return render_template('device_type_form.html', device_type=None)


@app.route('/device-types/<int:type_id>/edit', methods=['GET', 'POST'])
def edit_device_type(type_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))

    device_type = DeviceType.query.get_or_404(type_id)
    if request.method == 'POST':
        name = request.form.get('device_type', '').strip()
        if not name:
            flash('Device type is required.', 'danger')
            return render_template('device_type_form.html', device_type=device_type)

        device_type.device_type = name
        db.session.commit()
        flash('Device type updated.', 'success')
        return redirect(url_for('device_types'))

    return render_template('device_type_form.html', device_type=device_type)


@app.route('/device-types/<int:type_id>/delete', methods=['POST'])
def delete_device_type(type_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))

    device_type = DeviceType.query.get_or_404(type_id)
    db.session.delete(device_type)
    db.session.commit()
    flash('Device type deleted.', 'info')
    return redirect(url_for('device_types'))


@app.route('/categories')
def categories():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    categories = Category.query.order_by(Category.id).all()
    return render_template('categories.html', categories=categories)


@app.route('/categories/new', methods=['GET', 'POST'])
def new_category():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Category name is required.', 'danger')
            return render_template('category_form.html')

        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Category created.', 'success')
        return redirect(url_for('categories'))

    return render_template('category_form.html', category=None)


@app.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))

    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Category name is required.', 'danger')
            return render_template('category_form.html', category=category)

        category.name = name
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('categories'))

    return render_template('category_form.html', category=category)


@app.route('/categories/<int:category_id>/delete', methods=['POST'])
def delete_category(category_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))

    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted.', 'info')
    return redirect(url_for('categories'))


@app.route('/institutions')
def institutions():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    institutions = Institution.query.order_by(Institution.id).all()
    return render_template('institutions.html', institutions=institutions)


@app.route('/institutions/new', methods=['GET', 'POST'])
def new_institution():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Institution name is required.', 'danger')
            return render_template('institution_form.html')

        institution = Institution(name=name)
        db.session.add(institution)
        db.session.commit()
        flash('Institution created.', 'success')
        return redirect(url_for('institutions'))

    return render_template('institution_form.html', institution=None)


@app.route('/institutions/<int:institution_id>/edit', methods=['GET', 'POST'])
def edit_institution(institution_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))

    institution = Institution.query.get_or_404(institution_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Institution name is required.', 'danger')
            return render_template('institution_form.html', institution=institution)

        institution.name = name
        db.session.commit()
        flash('Institution updated.', 'success')
        return redirect(url_for('institutions'))

    return render_template('institution_form.html', institution=institution)


@app.route('/institutions/<int:institution_id>/delete', methods=['POST'])
def delete_institution(institution_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))

    institution = Institution.query.get_or_404(institution_id)
    db.session.delete(institution)
    db.session.commit()
    flash('Institution deleted.', 'info')
    return redirect(url_for('institutions'))


@app.route('/issues')
def issues():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    ticket_id = request.args.get('ticket_id', '').strip()
    agent_id = request.args.get('agent_id', '').strip()
    query = Issue.query
    if ticket_id:
        query = query.filter(Issue.issue_ticket_no.ilike(f'%{ticket_id}%'))
    if agent_id:
        query = query.filter(Issue.agent_name.ilike(f'%{agent_id}%'))
    issues = query.order_by(Issue.log_date.desc()).all()
    return render_template('issues.html', issues=issues, ticket_id=ticket_id, agent_id=agent_id)


@app.route('/issues/new', methods=['GET', 'POST'])
def new_issue():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    categories = Category.query.order_by(Category.name).all()
    institutions = Institution.query.order_by(Institution.name).all()

    if request.method == 'POST':
        issue_ticket_no = generate_ticket_number()
        diff_in_days = int(request.form.get('diff_in_days', 0))
        conformance_to_sla = request.form.get('conformance_to_sla', '').strip()
        terminal_id = request.form.get('terminal_id', '').strip()
        agent_name = request.form.get('agent_name', '').strip()
        log_date = datetime.fromisoformat(request.form.get('log_date')) if request.form.get('log_date') else datetime.utcnow()
        categoryname = request.form.get('categoryname', '').strip()
        issuedescription = request.form.get('issuedescription', '').strip()
        last_updated_on = datetime.utcnow()
        sla = request.form.get('sla', '').strip()
        status = request.form.get('status', '').strip()
        institutionalid = request.form.get('institutionalid', '').strip()
        createdbyname = session.get('username', 'unknown')
        location = request.form.get('location', '').strip() or agent_locations.get(agent_name, '')

        if not terminal_id or not agent_name or not categoryname or not issuedescription or not sla or not status or not institutionalid or not location:
            flash('Please fill all required issue fields.', 'danger')
            return render_template('issue_form.html', issue=None, categories=categories, institutions=institutions)

        issue = Issue(
            issue_ticket_no=issue_ticket_no,
            diff_in_days=diff_in_days,
            conformance_to_sla=conformance_to_sla,
            terminal_id=terminal_id,
            agent_name=agent_name,
            log_date=log_date,
            categoryname=categoryname,
            issuedescription=issuedescription,
            last_updated_on=last_updated_on,
            sla=sla,
            status=status,
            institutionalid=institutionalid,
            createdbyname=createdbyname,
            location=location,
        )
        db.session.add(issue)
        db.session.commit()
        flash(f'Issue created with ticket {issue_ticket_no}.', 'success')
        return redirect(url_for('issues'))

    return render_template('issue_form.html', issue=None, categories=categories, institutions=institutions)


@app.route('/issues/<issue_ticket_no>/edit', methods=['GET', 'POST'])
def edit_issue(issue_ticket_no):
    if not session.get('user_id'):
        return redirect(url_for('login'))

    issue = Issue.query.get_or_404(issue_ticket_no)
    categories = Category.query.order_by(Category.name).all()
    institutions = Institution.query.order_by(Institution.name).all()

    if request.method == 'POST':
        issue.diff_in_days = int(request.form.get('diff_in_days', issue.diff_in_days))
        issue.conformance_to_sla = request.form.get('conformance_to_sla', '').strip()
        issue.terminal_id = request.form.get('terminal_id', '').strip()
        issue.agent_name = request.form.get('agent_name', '').strip()
        issue.log_date = datetime.fromisoformat(request.form.get('log_date')) if request.form.get('log_date') else issue.log_date
        issue.categoryname = request.form.get('categoryname', '').strip()
        issue.issuedescription = request.form.get('issuedescription', '').strip()
        issue.last_updated_on = datetime.utcnow()
        issue.sla = request.form.get('sla', '').strip()
        issue.status = request.form.get('status', '').strip()
        issue.institutionalid = request.form.get('institutionalid', '').strip()
        issue.location = request.form.get('location', '').strip() or agent_locations.get(issue.agent_name, issue.location)

        if not issue.terminal_id or not issue.agent_name or not issue.categoryname or not issue.issuedescription or not issue.sla or not issue.status or not issue.institutionalid or not issue.location:
            flash('Please fill all required issue fields.', 'danger')
            return render_template('issue_form.html', issue=issue, categories=categories, institutions=institutions)

        db.session.commit()
        flash(f'Issue {issue.issue_ticket_no} updated.', 'success')
        return redirect(url_for('issues'))

    return render_template('issue_form.html', issue=issue, categories=categories, institutions=institutions)


@app.route('/issues/<issue_ticket_no>/delete', methods=['POST'])
def delete_issue(issue_ticket_no):
    if not session.get('user_id'):
        return redirect(url_for('login'))

    issue = Issue.query.get_or_404(issue_ticket_no)
    db.session.delete(issue)
    db.session.commit()
    flash('Issue deleted.', 'info')
    return redirect(url_for('issues'))


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
