from bottle import run, route, template

# in views there are templates

#base page
@route("/")
def home():
    return "hi"

lets_see_items = ["item1", "item2"]

#new page
@route("/extra")
def extra():
    return template("Extra", extra="Lets see", items=lets_see_items)

run(debug=True, reloader=True)