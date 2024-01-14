from flask import Flask, jsonify, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, URL

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


#Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns if getattr(self, column.name) is not None}


class CafeForm(FlaskForm):
    cafe = StringField('Cafe name', validators=[DataRequired()])
    local_url = StringField('Location URL', validators=[DataRequired(), URL()])
    img_url = StringField('Image (as URL)', validators=[DataRequired(), URL()])
    location = StringField('Area of London', validators=[DataRequired()])
    coffee_price = StringField('Coffee Price', validators=[DataRequired()])
    wifi = SelectField('Has Wi-Fi', choices=["True", "False", ], validators=[DataRequired()])
    power = SelectField('Has Charging',  choices=["True", "False", ], validators=[DataRequired()])
    toilet = SelectField('Has Toilets', choices=["True", "False", ], validators=[DataRequired()])
    calls = SelectField('Calls Allowed', choices=["True", "False", ], validators=[DataRequired()])
    submit = SubmitField('Submit')


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    all_cafes = Cafe.query.all()
    list_of_cafes = [cafe.to_dict() for cafe in all_cafes]
    return render_template("index.html", cafes=list_of_cafes)

@app.route("/detail/<int:cafe_id>")
def detail(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    return render_template("detail.html", cafe=cafe)


@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        try:
            new_cafe = Cafe(
                name=form.cafe.data,
                map_url=form.local_url.data,
                img_url=form.img_url.data,
                location=form.location.data,
                coffee_price=form.coffee_price.data,
                has_wifi=form.wifi.data == 'True',
                has_sockets=form.power.data == 'True',
                has_toilet=form.toilet.data == 'True',
                can_take_calls=form.calls.data == 'True',
            )
            db.session.add(new_cafe)
            db.session.commit()

            flash('Cafe added successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            print(f"Exception during form processing: {e}")
            flash('An error occurred while processing the form. Please try again.', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error in field "{getattr(form, field).label.text}": {error}', 'error')

    return render_template('add.html', form=form)

@app.route('/delete/<int:cafe_id>', methods=['POST'])
def delete_cafe(cafe_id):
    if request.method == 'POST':
        try:
            cafe_to_delete = Cafe.query.get(cafe_id)
            if cafe_to_delete:
                db.session.delete(cafe_to_delete)
                db.session.commit()
                flash('Cafe deleted successfully!', 'success')
            else:
                flash('Cafe not found.', 'error')
        except Exception as e:
            db.session.rollback()
            print(f"Exception during cafe deletion: {e}")
            flash('An error occurred while deleting the cafe. Please try again.', 'error')

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
