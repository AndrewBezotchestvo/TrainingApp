#коментарий

from flask import (
    Flask, render_template, request, redirect, url_for, flash, abort,
)
from flask_wtf.csrf import CSRFProtect

from models import db, Exercise, ExerciseLog
from forms import ExerciseForm, DeleteForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-me-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
csrf = CSRFProtect(app)

with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    """Главная: форма добавления + список упражнений."""
    form = ExerciseForm()
    delete_form = DeleteForm()

    if form.validate_on_submit():
        name = form.name.data.strip()
        category = form.category.data
        value = float(form.value.data)
        reps = int(form.reps.data) if form.reps.data else None

        if category == 'cardio':
            reps = None

        # Поиск без учёта регистра — через Python, т.к. SQLite LOWER()
        # не работает с кириллицей
        name_normalized = name.lower()
        existing = None
        for ex in Exercise.query.all():
            if ex.name.strip().lower() == name_normalized:
                existing = ex
                break

        if existing:
            old_value = existing.value
            existing.category = category
            existing.value = value
            existing.reps = reps
            db.session.add(ExerciseLog(
                exercise_id=existing.id, value=value, reps=reps,
            ))
            db.session.commit()

            unit = 'км' if category == 'cardio' else 'кг'
            flash(
                f'"{existing.name}": обновлено с {old_value:g} до {value:g} {unit}',
                'success',
            )
        else:
            exercise = Exercise(name=name, category=category, value=value, reps=reps)
            db.session.add(exercise)
            try:
                db.session.flush()
            except IntegrityError:
                db.session.rollback()
                # Кто-то вставил параллельно — ищем и обновляем
                existing = None
                for ex in Exercise.query.all():
                    if ex.name.strip().lower() == name_normalized:
                        existing = ex
                        break
                if existing:
                    existing.category = category
                    existing.value = value
                    existing.reps = reps
                    db.session.add(ExerciseLog(
                        exercise_id=existing.id, value=value, reps=reps,
                    ))
                    db.session.commit()
                    flash(f'"{existing.name}": обновлено до {value:g}', 'success')
                else:
                    flash('Не удалось сохранить, попробуйте ещё раз', 'error')
            else:
                db.session.add(ExerciseLog(
                    exercise_id=exercise.id, value=value, reps=reps,
                ))
                db.session.commit()
                flash(f'Упражнение "{name}" добавлено', 'success')

        return redirect(url_for('index'))

    if request.method == 'POST':
        for field_errors in form.errors.values():
            for error in field_errors:
                flash(error, 'error')

    exercises = Exercise.query.order_by(Exercise.name).all()
    strength = [e for e in exercises if e.category == 'strength']
    cardio = [e for e in exercises if e.category == 'cardio']

    return render_template(
        'index.html',
        form=form,
        delete_form=delete_form,
        strength=strength,
        cardio=cardio,
        total=len(exercises),
    )


@app.route('/exercise/<int:exercise_id>/delete', methods=['POST'])
def delete_exercise(exercise_id):
    form = DeleteForm()
    if not form.validate_on_submit():
        abort(400)

    exercise = Exercise.query.get_or_404(exercise_id)
    name = exercise.name
    db.session.delete(exercise)
    db.session.commit()
    flash(f'Упражнение "{name}" удалено', 'success')
    return redirect(url_for('index'))


@app.route('/exercise/<int:exercise_id>/history')
def exercise_history(exercise_id):
    """Страница с историей изменения веса/дистанции."""
    exercise = Exercise.query.get_or_404(exercise_id)
    return render_template('history.html', exercise=exercise)


if __name__ == '__main__':
    app.run(debug=True)