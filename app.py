
#rota home
@app.get('/', tags = [home_tag])
def documentation():
    '''
        Redireciona para /openapi, tela que permite a escolha do estilo
        de documentação.
    '''
    return redirect('/openapi')

#rota create
@app.post('/create', tags = [create_tag])
def create():
    #obrigatórios: name, description, interval
    #opcionais: send_email, recurring, image
    try:
        prepare_description = new Description(form.description)
        prepare_image = new Image(form.image)
        reminder = Reminder(
            name = form.name,
            description = prepare_description,
            interval = form.interval
            send_email = form.send_email,
            recurring = form.recurring,
            image = prepare_image
        )

    except:

#rota edit / update - a rota edit será o equivalente a show
@app.put('/update', tags = [update_tag])
def update():

#rota show all
@app.get('/show_all', tags = [show_all_tag])
def show_all():

#rota delete
@app.delete('/delete', tags = [delete_tag])
def delete():
