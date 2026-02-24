const QRCode = require('qrcode');
const fs = require('fs');

async function generateQR() {
    const url = 'https://forms.gle/UCcSsrNpcUVbDMoW9';
    const path = '/home/claw/.openclaw/workspace/qrcode_google_form.png';
    
    try {
        await QRCode.toFile(path, url, {
            color: {
                dark: '#000000',
                light: '#FFFFFF'
            },
            width: 1024
        });
        console.log('QR Code saved to ' + path);
    } catch (err) {
        console.error(err);
    }
}

generateQR();
