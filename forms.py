from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, DecimalField, IntegerField, SubmitField,
)
from wtforms.validators import (
    DataRequired, Optional, NumberRange, Length, ValidationError,
)


class ExerciseForm(FlaskForm):
    """Форма добавления/обновления упражнения на главной."""
    name = StringField(
        'Упражнение',
        validators=[DataRequired(message='Укажите название'), Length(max=120)],
    )
    category = SelectField(
        'Тип',
        choices=[('strength', 'Силовое'), ('cardio', 'Кардио')],
        validators=[DataRequired()],
    )
    value = DecimalField(
        'Текущий вес (кг) / дистанция (км)',
        places=2,
        validators=[
            DataRequired(message='Укажите вес или дистанцию'),
            NumberRange(min=0.01, message='Значение должно быть больше 0'),
        ],
    )
    reps = IntegerField(
        'Повторы (для силовых)',
        validators=[Optional(), NumberRange(min=1, max=1000)],
    )
    submit = SubmitField('Сохранить')

    def validate_name(self, field):
        cleaned = (field.data or '').strip()
        if not cleaned:
            raise ValidationError('Название не может быть пустым')
        field.data = cleaned

    def validate_reps(self, field):
        if self.category.data == 'strength' and not field.data:
            raise ValidationError('Для силового упражнения укажите повторы')


class DeleteForm(FlaskForm):
    """Пустая форма только для CSRF-токена."""
    submit = SubmitField('Удалить')