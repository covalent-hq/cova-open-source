require('dotenv').config();
const mandrill = require('mandrill-api/mandrill');
const mandrill_client = new mandrill.Mandrill(process.env.MANDRILL_KEY);

const sendEmail = async (user) => {
  // TO-DO: change thi in prod
  let url = '';
  if (process.env.DOMAIN === 'localhost:3000') {
    url = `http://${process.env.DOMAIN}/verify/${user.hash}`;
  } else {
    url = `https://${process.env.DOMAIN}/verify/${user.hash}`;
  }
  const msg = 'Please click here to verify your email: ' + url;

  let message = {
  "html": `<h2>${msg}</h2>`,
  "text": msg,
  "subject": "Account verification",
  "from_email": "noreply@covalent.ai",
  "from_name": "Covalent Admin",
  "to": [{
        "email":  user.email,
        "type": "to"
  }],
  "headers": {
          "Reply-To": "admin@covalent.ai"
  },
  "important": true,
  "track_opens": true,
  "track_clicks": true,
  "auto_text": null,
  "auto_html": true,
  "inline_css": null,
  "url_strip_qs": null,
  "preserve_recipients": null,
  "view_content_link": null,
  "tracking_domain": null,
  "signing_domain": 'covalent.ai',
  "return_path_domain": null,
  "tags": [
    "user-account-verification"
  ]
}

  let async = true;
  let ip_pool = "Main Pool";
  await mandrill_client.messages.send({"message": message, "async": async, "ip_pool": ip_pool}, function(result) {
    if(result[0].status === 'sent'){
      return true;
    }
    return false;
  }, function(e) {
    console.log('A mandrill error occurred: ' + e.name + ' - ' + e.message);
  });
};

const sendCreds = async (user) => {
  // TO-DO: change thi in prod
  const msg = `
    <h3>id: ${user.email}</h3>
    <h3>Eth</h3>
    <p>Address: ${user.eth_cred.address} <br> Private Key: ${user.eth_cred.privateKey}</p><br>
    <h3>Bigchandb</h3>
    <p>Public Key: ${user.bdb_cred.publicKey} <br> Private Key: ${user.bdb_cred.privateKey}</p><br>
    <h3>RSA</h3>
    <p>Public Key: ${user.rsa_cred.publicKey} <br><br> Private Key: ${user.rsa_cred.privateKey}</p><br>
    `;

  const content = {
    id: user.email,
    eth_cred: {
      address: user.eth_cred.address,
      privateKey: user.eth_cred.privateKey
    },
    bdb_cred: {
      publicKey: user.bdb_cred.publicKey,
      privateKey: user.bdb_cred.privateKey
    },
    rsa_cred: {
      publicKey: user.rsa_cred.publicKey,
      privateKey: user.rsa_cred.privateKey
    },
    public_ip: "YOUR-PUBLIC-IP:PORT",
    sgx: 0,
    router: 0
  };
  const file_content = JSON.stringify(content);
  let message = {
  "html": `<div>${msg}</div>`,
  "text": msg,
  "subject": "Covalent: FakeCova Faucet Credentials",
  "from_email": "noreply@covalent.ai",
  "from_name": "Covalent Admin",
  "to": [{
        "email":  user.email,
        "type": "to"
  }],
  "headers": {
          "Reply-To": "admin@covalent.ai"
  },
  "attachments": [{
    "type": "text/json",
    "name": "usercred.json",
    "content": Buffer.from(file_content).toString('base64')
  }],
  "important": true,
  "track_opens": true,
  "track_clicks": true,
  "auto_text": null,
  "auto_html": true,
  "inline_css": null,
  "url_strip_qs": null,
  "preserve_recipients": null,
  "view_content_link": null,
  "tracking_domain": null,
  "signing_domain": 'covalent.ai',
  "return_path_domain": null,
  "tags": [
    "user-account-verification"
  ]
}

  let async = true;
  let ip_pool = "Main Pool";
  await mandrill_client.messages.send({"message": message, "async": async, "ip_pool": ip_pool}, function(result) {
    if(result[0].status === 'sent'){
      return true;
    }
    return false;
  }, function(e) {
    console.log('A mandrill error occurred: ' + e.name + ' - ' + e.message);
  });
};

module.exports = {
  sendEmail,
  sendCreds
}
