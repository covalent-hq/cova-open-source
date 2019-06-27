var app = require('express')()
var routes = require('./routes/routes')
app.set('json spaces', 4)

var bodyParser = require('body-parser');
app.use(bodyParser.json()); 
app.use(bodyParser.urlencoded({ extended: true })); 

app.use('/', routes)
app.listen(5001)

console.log('Cova Bighcaidb API is Running')
