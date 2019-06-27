var app = require('express')()
var coinRoutes = require('./routes/coinRoutes')
var paymentRoutes = require('./routes/paymentRoutes')
var faucetRoutes = require('./routes/faucetRoutes')

app.set('json spaces', 4)

app.use('/covaCoin', coinRoutes)
app.use('/payment', paymentRoutes)
app.use('/faucet', faucetRoutes)

app.listen(5000)

console.log('The cova API is running')
