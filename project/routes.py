@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()

if form.validate_on_submit():
    try:
        email = form.email.data
        pwd = form.pwd.data
        username = form.username.data
        
        newuser = User(
            username=username,
            email=email,
            pwd=bcrypt.generate_password_hash(pwd),
            )
    
        db.session.add(newuser)
        db.session.commit()
        flash(f"Account Succesfully created", "success")
        return redirect(url_for("login"))

    except Exception as e:
        flash(e, "danger")

if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

# Home route
@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    return render_template("index.html",title="Home")

# Login route
@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    return render_template("auth.html",form=form)

# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()

    return render_template("auth.html",form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
 
if __name__ == "__main__":
    app.run(debug=True)