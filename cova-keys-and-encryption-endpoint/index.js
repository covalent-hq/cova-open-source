var app = require('express')()
var routes = require('./routes/routes')
app.set('json spaces', 4)
var bodyParser = require('body-parser')

app.use( bodyParser.json() );
app.use(bodyParser.urlencoded({
  extended: true
})); 

app.use('/', routes)
app.listen(5002)
console.log('Cova Encryption Enpoint is Running')
