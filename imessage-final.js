#!/usr/bin/env node

const { exec } = require('child_process');

let lastId = 118; // Start after your last message
console.log('Starting monitor from ID:', lastId);

function checkMessages() {
    exec('imsg history --chat-id 1 --limit 3 --json', (error, stdout) => {
        if (error) return;
        
        const lines = stdout.trim().split('\n');
        for (const line of lines) {
            if (!line.trim().startsWith('{')) continue;
            
            try {
                const msg = JSON.parse(line);
                if (msg.id <= lastId || msg.is_from_me || !msg.text) continue;
                
                console.log('New message:', msg.id, msg.text);
                
                // Send response
                const text = msg.text.toLowerCase();
                let response = 'Got your message! iMessage integration is working.';
                
                if (text.includes('stock')) {
                    response = 'For stocks, I recommend KLAC, LRCX, and AVGO right now.';
                } else if (text.includes('test')) {
                    response = 'Test successful! iMessage automation is working perfectly.';
                }
                
                exec(`imsg send --to "+14044160690" --text "${response}"`, (err) => {
                    if (!err) console.log('Response sent');
                });
                
                lastId = msg.id;
                
            } catch (e) {
                // Skip bad JSON
            }
        }
    });
}

setInterval(checkMessages, 3000);
console.log('Monitoring started...');