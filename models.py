from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Exercise(db.Model):
    """Упражнение с текущим рабочим значением."""
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    category = db.Column(db.String(20), default='strength')  # 'strength' | 'cardio'
    value = db.Column(db.Float, nullable=False)  # текущий вес (кг) или дистанция (км)
    reps = db.Column(db.Integer, nullable=True)  # повторы для силовых
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    history = db.relationship(
        'ExerciseLog',
        backref='exercise',
        cascade='all, delete-orphan',
        lazy=True,
        order_by='ExerciseLog.created_at.desc()',
    )

    @property
    def is_cardio(self):
        return self.category == 'cardio'

    @property
    def display_value(self):
        return f'{self.value:g} км' if self.is_cardio else f'{self.value:g} кг'

    def __repr__(self):
        return f'<Exercise {self.name}={self.value}>'


class ExerciseLog(db.Model):
    """История изменений — каждый раз, когда обновляешь вес/дистанцию."""
    __tablename__ = 'exercise_logs'

    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    reps = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Log {self.exercise_id}: {self.value}>'