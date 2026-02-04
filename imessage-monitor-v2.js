#!/usr/bin/env node
/**
 * iMessage Monitor V2 for OpenClaw
 * Robust message parsing with encoding fixes
 */

const { exec } = require('child_process');
const fs = require('fs');

class iMessageMonitor {
    constructor() {
        this.chatId = 1;
        this.phoneNumber = '+14044160690';
        this.lastMessageId = this.loadLastMessageId();
        this.isRunning = false;
        
        console.log(`🔍 iMessage Monitor V2 starting - Last message ID: ${this.lastMessageId}`);
    }
    
    async start() {
        this.isRunning = true;
        
        // Send startup notification
        this.sendReply('🔍 Scout iMessage Monitor is now LIVE! Send me messages and I\'ll respond automatically.');
        
        // Get baseline if needed
        if (this.lastMessageId === 0) {
            await this.getBaseline();
        }
        
        console.log('👀 Monitoring iMessages every 2 seconds...');
        this.startPolling();
    }
    
    async getBaseline() {
        return new Promise((resolve) => {
            exec(`imsg history --chat-id ${this.chatId} --limit 1 --json`, (error, stdout) => {
                if (!error && stdout.trim()) {
                    try {
                        const lines = stdout.trim().split('\\n').filter(line => line.trim());
                        if (lines.length > 0) {
                            const message = JSON.parse(lines[0]);
                            this.lastMessageId = message.id;
                            this.saveLastMessageId();
                            console.log(`📱 Baseline set to message ID: ${this.lastMessageId}`);
                        }
                    } catch (e) {
                        console.log('📱 Starting with fresh baseline');
                    }
                }
                resolve();
            });
        });
    }
    
    startPolling() {
        this.pollInterval = setInterval(() => {
            if (this.isRunning) {
                this.checkForNewMessages();
            }
        }, 2000);
    }
    
    checkForNewMessages() {
        exec(`imsg history --chat-id ${this.chatId} --limit 5 --json`, (error, stdout) => {
            if (error) {
                console.error('❌ Error checking messages:', error.message);
                return;
            }
            
            if (!stdout.trim()) return;
            
            try {
                const lines = stdout.trim().split('\\n').filter(line => {
                    const cleanLine = line.trim();
                    return cleanLine && cleanLine.startsWith('{') && cleanLine.endsWith('}');
                });
                const newMessages = [];
                
                for (const line of lines) {
                    try {
                        // Clean the JSON string before parsing
                        const cleanJson = line.replace(/[\\u0000-\\u001f]/g, '');
                        const message = JSON.parse(cleanJson);
                        
                        // Clean up text encoding issues
                        if (message.text) {
                            message.text = message.text.replace(/[\\u0000-\\u001f]/g, '').trim();
                        }
                        
                        // Skip if old message or from us
                        if (message.id <= this.lastMessageId || message.is_from_me) {
                            continue;
                        }
                        
                        newMessages.push(message);
                        
                    } catch (parseError) {
                        // Skip malformed JSON
                        continue;
                    }
                }
                
                // Process new messages in chronological order (oldest first)
                newMessages.reverse();
                for (const message of newMessages) {
                    console.log(`📨 NEW MESSAGE [${message.id}]: "${message.text}"`);
                    this.processMessage(message);
                    this.lastMessageId = message.id;
                    this.saveLastMessageId();
                }
                
            } catch (e) {
                console.error('❌ Error processing messages:', e.message);
            }
        });
    }
    
    processMessage(message) {
        if (!message.text || message.text.trim().length === 0) {
            console.log('⚠️ Empty message, skipping');
            return;
        }
        
        const userMessage = message.text.trim();
        console.log(`🤔 Processing: "${userMessage}"`);
        
        // Send immediate acknowledgment
        this.sendReply('🔍 Got your message, processing...');
        
        // Create a simple response for now (we'll enhance this)
        this.generateResponse(userMessage, (response) => {
            if (response) {
                this.sendReply(response);
            }
        });
    }
    
    generateResponse(userMessage, callback) {
        // For now, let's create intelligent responses based on message content
        const msg = userMessage.toLowerCase();
        
        if (msg.includes('stock') || msg.includes('invest') || msg.includes('market')) {
            callback('📊 Investment query detected! I can help with stock research, market analysis, and portfolio recommendations. What specific stock or sector are you interested in?');
        } else if (msg.includes('hello') || msg.includes('hi') || msg.includes('hey')) {
            callback('👋 Hey! Scout here - your personal investment research assistant. I can help with stock analysis, market research, and daily portfolio updates. What can I look into for you?');
        } else if (msg.includes('test')) {
            callback('✅ iMessage integration is working perfectly! I can now receive and respond to your messages automatically. Try asking me about stocks or market research!');
        } else if (msg.includes('report') || msg.includes('research')) {
            callback('📈 Your daily 8 AM investment research reports are scheduled and ready! I can also provide real-time stock analysis, market trends, and investment opportunities on demand.');
        } else {
            // Default intelligent response
            callback(`🔍 Message received: "${userMessage}" - iMessage monitoring is working! I'm Scout, your investment research assistant. Try asking me about stocks, market analysis, or investment opportunities!`);
        }
    }
    
    sendReply(text) {
        const cleanText = text.replace(/"/g, '\\\\"');
        const sendCommand = `imsg send --to "${this.phoneNumber}" --text "${cleanText}"`;
        
        exec(sendCommand, (error) => {
            if (error) {
                console.error('❌ Error sending reply:', error.message);
            } else {
                console.log(`✅ Sent: "${text.substring(0, 80)}${text.length > 80 ? '...' : ''}"`);
            }
        });
    }
    
    loadLastMessageId() {
        try {
            if (fs.existsSync('imsg-state.json')) {
                const state = JSON.parse(fs.readFileSync('imsg-state.json', 'utf8'));
                return state.lastMessageId || 0;
            }
        } catch (e) {
            console.error('Error loading state:', e.message);
        }
        return 0;
    }
    
    saveLastMessageId() {
        try {
            const state = { 
                lastMessageId: this.lastMessageId, 
                timestamp: Date.now(),
                lastUpdate: new Date().toISOString()
            };
            fs.writeFileSync('imsg-state.json', JSON.stringify(state, null, 2));
        } catch (e) {
            console.error('Error saving state:', e.message);
        }
    }
    
    stop() {
        this.isRunning = false;
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }
        console.log('🛑 iMessage Monitor stopped');
    }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\\n🛑 Shutting down gracefully...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\\n🛑 Received SIGTERM, shutting down...');
    process.exit(0);
});

// Start monitoring
console.log('🚀 Starting iMessage Monitor V2...');
const monitor = new iMessageMonitor();
monitor.start().catch(console.error);