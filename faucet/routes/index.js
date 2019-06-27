const express = require('express');
const router = express.Router();
const db = require('../db/index');
const { body } = require('express-validator/check');
const { sanitizeBody } = require('express-validator/filter');
const { check, validationResult } = require('express-validator/check');
const Mailer = require('../controller/Mailer');
const fetch = require('node-fetch');
require('dotenv').config();
const requestIp = require('request-ip');

// const config = require('../config').config_local;

// const Recaptcha = require('express-recaptcha').Recaptcha;
// const options = {'theme':'light'};
// const recaptcha = new Recaptcha(config.SITE_KEY_TEST, config.SECRET_KEY_TEST, options);

/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index');
});

// POST data from input form
router.post('/form-submit', [
    body('username')
      .not().isEmpty()
      .trim()
      .escape(),
    body('email')
      .isEmail()
      .normalizeEmail(),
    body('company')
      .trim()
      .escape(),
    body('description')
      .trim()
      .escape(),
    sanitizeBody('notifyOnReply').toBoolean()
], async (req, res) => {
  let username = req.sanitize(req.body.username);
  let email = req.sanitize(req.body.email);
  let company = req.sanitize(req.body.company);
  let description = req.sanitize(req.body.description);
  const captcha = req.body.captcha;
  const isVerified = await verifyCaptcha(captcha, req);
  // console.log("isVerifed = ", isVerified);
  // check for errors
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
   return res.status(422).json({ errors: errors.array() });
  }

  //insert data into db only if captcha verified
  if (isVerified === true) {
    try {
      const result = await db.createNewUser({username, email, company, description});
      if(result.error === "unique_email"){
        res.render('error', {error: 'This email has already been used.'});
      } else {
        res.send(`Please verify your email. <br/> Didn't get email? <a href='/send_email/${result.id}/${result.hash}'> Send Again </a>`);
      }
    } catch (err) {
      let err_msg = err.constraint || "Error. Please try again";
       if(err.constraint === 'unique_email'){
         err_msg = 'This email has already been used.';
       }
      console.log("Error in /form-submit", err);
      res.render('error' , {error: err_msg});
    }
  } else {
    res.render('error', {error: 'Wow! You are a robot! Bye. :)'});
  }

});

router.get('/send_email/:id/:hash', async (req, res) => {
  const email = await db.getEmail(req.params.id);
  await Mailer.sendEmail({ id: req.params.id, email: email, hash: req.params.hash });
  res.send(`Please verify your email. <br/> Didn't get email? <a href='/send_email/${req.params.id}/${req.params.hash}'> Send Again </a>`);
});

//verify signup user (email verification)
router.get('/verify/:hash', async (req, res, next) => {
    let result;
    const hash = req.params.hash;
    const isValid = await db.verifyUser(hash);
    if(isValid){
      const isCredExists = await db.isCredExists(hash);
      if (isCredExists === false) {
        // result = await db.generateCredentials(hash);
        db.generateCredentials(hash);
        res.send(`Successfully registered! Please check your email for credentials.`);
      } else {
        res.send('Your account already exists. Please check inbox/spam.');
      }
    } else {
      res.send(`Please verify your email.`);
    }
});

// check balance
router.get('/checkbalance/:address', async (req, res) => {
  const address = req.params.address;
  const url = `${process.env.BALANCE_URL}/${address}`;
  // console.log("url=", url);
  try {
    const result = await fetch(url);
    let data = await result.json();
    data = (data === undefined) ? 0 : data;
    res.send({balance: data});
  } catch (e) {
    console.log("Error in check baalnce: ", e);
    res.send({balance: 0});
  }
});

router.post('/verify-captcha', async (req, res) => {
  const captcha = req.body.captcha;
  try {
    const isVerified = await verifyCaptcha(captcha, req);
    if (isVerified === true) {
      res.send(true);
    } else {
      res.send(false);
    }
  } catch (e) {
    console.log("Error in verify-captcha: ", e);
    res.send(false);
  }

});


const verifyCaptcha = async (captcha, req) => {
  const secret_key = process.env.CAPTCHA_SECRET_KEY;
  // using test key for local
  // must change in prod
  const clientIp = requestIp.getClientIp(req);
  const url = `https://www.google.com/recaptcha/api/siteverify?secret=${secret_key}&response=${captcha}&remoteip=${clientIp}`;
  try {
    const response = await fetch(url);
    const result = await response.json();
    if (result.success === true) {
      return true;
    } else {
      return false;
    }
  } catch (e) {
    return false;
  }
}

module.exports = router;
