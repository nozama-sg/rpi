const localtunnel = require('localtunnel');
const fs = require('fs');

(async () => {
    const tunnel = await localtunnel({ port: 5000 });  

    fs.writeFileSync('tunnelURL.txt', tunnel.url);

    tunnel.on('close', () => {
        // tunnels are closed
        console.log('Tunnel Closed');
  }); 
})();
