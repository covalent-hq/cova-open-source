const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');
const url = require('url');
const Mailer = require('../controller/Mailer');
require('dotenv').config();
const crypto = require('crypto');
const bcrypt = require('bcrypt');
const saltRounds = 10;
const fetch = require('node-fetch');

let params = url.parse(process.env.DB_PARAMS);
let auth = params.auth.split(':');

const config_local = {
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  database: process.env.DB_DATABASE,
  max: 10,
  idleTimeoutMillis: 5000
}

const config_prod = {
    user: auth[0],
    password: auth[1],
    host: params.hostname,
    port: params.port,
    database: params.pathname.split('/')[1],
    ssl: {
      ca: [fs.readFileSync(path.join(__dirname, '..', 'config', 'amazon-rds-ca-cert.pem')).toString()]
    },
    // https://serverfault.com/questions/862387/aws-rds-connection-limits
    max: 50,
    idleTimeoutMillis: 10000
}

const pool = new Pool(config_prod);

const getAllUsers = async () => {
  const queryStr = 'SELECT * FROM public_net_users';
  try {
    const res = await pool.query(queryStr);
    return res.rows;
  } catch (err) {
    console.log("Error in getAllUsers(): ", err);
  }
}

const createNewUser = async (data) => {
  const current_date = (new Date()).valueOf().toString();
  let hash = crypto.createHash('md5').update(current_date).digest('hex');
  hash = hash.replace('/','');

  const queryStr = `
    INSERT INTO public_net_users
    (username, email, company, description, hash)
    VALUES (
      '${data.username}',
      '${data.email}',
      '${data.company}',
      '${data.description}',
      '${hash}'
    ) RETURNING *
  `;

  try {
    const res = await pool.query(queryStr);
    await Mailer.sendEmail({id: res.rows[0].id, email: data.email, hash: hash});
    return res.rowCount > 0 ? { id: res.rows[0].id, hash: hash } : false;
  } catch (err) {
    if (err.constraint === 'unique_email') {
      return {error: err.constraint};
    } else {
      console.log("Error in createNewUser", err);
      return false;
    }
  }
}


const isCredExists = async (hash) => {
    const queryStr = `select eth_private_key, eth_address from public_net_users where hash = '${hash}'`;
    try {
      const result = await pool.query(queryStr);
      if(result.rows[0].eth_private_key === null || result.rows[0].eth_address === null) {
        return false;
      } else {
        return true;
      }
    } catch (err) {
      console.log('Error in isCredExists()', err);
      return false;
    }
}

const verifyUser = async (hash) => {
  const updateUserStr = `UPDATE public_net_users SET is_verified=true WHERE hash='${hash}'`;
  try {
      const updateRes = await pool.query(updateUserStr);
      return updateRes.rowCount > 0 ? true : false;
  } catch(err) {
    console.log("Error in verifyUser", err);
    return false;
  }
}

const getEmail = async (id) => {
  const queryStr = `SELECT email FROM public_net_users WHERE id = ${id}`;
  try {
    const res = await pool.query(queryStr);
    return res.rows[0].email;
  } catch (err) {
    console.log("Error in getEmail(): ", err);
  }
}

const getEmailByHash = async (hash) => {
  const queryStr = `SELECT email FROM public_net_users WHERE hash = '${hash}'`;
  // console.log(queryStr);
  try {
    const res = await pool.query(queryStr);
    return res.rows[0].email;
  } catch (err) {
    console.log("Error in getEmail(): ", err);
  }
}

const generateCredentials = async (hash) => {
  const url = process.env.CRED_URL;
  const email = await getEmailByHash(hash);
  try {
    const result = await fetch(url, {
      headers: { 'authorization':  'RuiMachKheteMoja'}
    });
    const data = await result.json();
    console.log(data);
    const queryStr = `
      UPDATE public_net_users SET
      eth_address='${data.eth_cred.address}',
      eth_private_key='${data.eth_cred.privateKey}',
      bdb_public_key='${data.bdb_cred.publicKey}',
      bdb_private_key='${data.bdb_cred.privateKey}',
      rsa_public_key='${data.rsa_cred.publicKey}',
      rsa_private_key='${data.rsa_cred.privateKey}'
      WHERE email='${email}' RETURNING *`;
    // console.log(queryStr);
    const res = await pool.query(queryStr);
    Mailer.sendCreds({id: res.rows[0].id, email: email, eth_cred: data.eth_cred, bdb_cred: data.bdb_cred, rsa_cred: data.rsa_cred});
    return { id: res.rows[0].id, hash: res.rows[0].hash};
  } catch (e) {
    console.log("Error in generateCredentials(): ", e);
    return false;
  }
}

// just call once to fill in the DB
// const runMigration = async () => {
//   const createTableQuery = `CREATE TABLE public_net_users (
//       id SERIAL CONSTRAINT public_net_user_primary_id PRIMARY KEY,
//       username VARCHAR(100),
//       email VARCHAR(100),
//       company VARCHAR(100),
//       description TEXT,
//       created_at TIMESTAMP WITHOUT TIME zone NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
//   );`;
//
//   const alterTableQuery1 = `ALTER TABLE public_net_users ADD CONSTRAINT public_net_unique_email UNIQUE (email);`;
//   const alterTableQuery2 = `ALTER TABLE public_net_users ADD COLUMN is_verified boolean DEFAULT false;`;
//   const alterTableQuery3 = `ALTER TABLE public_net_users ADD COLUMN hash VARCHAR(255);`;
//   const alterTableQuery4 = `ALTER TABLE public_net_users ADD COLUMN address VARCHAR(255);`;
//   const alterTableQuery5 = `ALTER TABLE public_net_users ADD COLUMN private_key VARCHAR(255);`;
//
//   // ALTER TABLE table_name RENAME COLUMN column_name TO new_column_name;
//   const alterTableQuery6 = 'ALTER TABLE public_net_users RENAME COLUMN address TO eth_address';
//   const alterTableQuery7 = 'ALTER TABLE public_net_users RENAME COLUMN private_key TO eth_private_key';
//   const alterTableQuery10 = 'ALTER TABLE public_net_users ADD COLUMN bdb_public_key TEXT;';
//   const alterTableQuery11 = 'ALTER TABLE public_net_users ADD COLUMN bdb_private_key TEXT';
//   const alterTableQuery12 = 'ALTER TABLE public_net_users ADD COLUMN rsa_public_key TEXT;';
//   const alterTableQuery13 = 'ALTER TABLE public_net_users ADD COLUMN rsa_private_key TEXT;';
//
//   const testQuery = ` select column_name, data_type, character_maximum_length
//  from INFORMATION_SCHEMA.COLUMNS where table_name ='public_net_users';`;
//  const testQuery2 = `select * from public_net_users`;
//
//  const delQuery = "delete from public_net_users where email = 'shariarabrar@gmail.com'";
//   try {
//     // await pool.query(createTableQuery);
//     // await pool.query(alterTableQuery1);
//     // await pool.query(alterTableQuery2);
//     // await pool.query(alterTableQuery3);
//     // await pool.query(alterTableQuery4);
//     // await pool.query(alterTableQuery5);
//     // await pool.query(alterTableQuery6);
//     // await pool.query(alterTableQuery7);
//     // await pool.query(alterTableQuery10);
//     // await pool.query(alterTableQuery11);
//     // await pool.query(alterTableQuery12);
//     // await pool.query(alterTableQuery13);
//     const result = await pool.query(delQuery);
//     console.log(result);
//   } catch (e) {
//     console.log("Error in run Migration()",e);
//   }
// }
//
// (() => {
//     runMigration();
// })();


module.exports = {
  getAllUsers,
  createNewUser,
  verifyUser,
  getEmail,
  generateCredentials,
  getEmailByHash,
  isCredExists
}
