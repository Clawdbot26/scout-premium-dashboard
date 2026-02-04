#!/usr/bin/env node
/**
 * Simple iMessage Monitor for OpenClaw
 * Polls for new messages and responds via OpenClaw session
 */

const { exec } = require('child_process');
const fs = require('fs');

class SimpleMessageMonitor {
    constructor() {
        this.chatId = 1;
        this.phoneNumber = '+14044160690';
        this.lastMessageId = this.loadLastMessageId();
        this.isRunning = false;
        
        console.log(`🔍 Starting iMessage Monitor - Last message ID: ${this.lastMessageId}`);
    }
    
    async start() {
        this.isRunning = true;
        
        // Get baseline if we don't have one
        if (this.lastMessageId === 0) {
            await this.getBaseline();
        }
        
        console.log('👀 Monitoring iMessages every 3 seconds...');
        this.startPolling();
    }
    
    async getBaseline() {
        return new Promise((resolve) => {
            exec(`imsg history --chat-id ${this.chatId} --limit 1 --json`, (error, stdout) => {
                if (!error && stdout.trim()) {
                    try {
                        const message = JSON.parse(stdout.trim().split('\\n')[0]);
                        this.lastMessageId = message.id;
                        this.saveLastMessageId();
                        console.log(`📱 Baseline set to message ID: ${this.lastMessageId}`);
                    } catch (e) {
                        console.log('📱 No previous messages found, starting fresh');
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
        }, 3000);
    }
    
    checkForNewMessages() {
        exec(`imsg history --chat-id ${this.chatId} --limit 3 --json`, (error, stdout) => {
            if (error) {
                console.error('❌ Error checking messages:', error.message);
                return;
            }
            
            if (!stdout.trim()) return;
            
            try {
                const lines = stdout.trim().split('\\n').filter(line => line.trim());
                
                for (const line of lines) {
                    let message;
                    try {
                        message = JSON.parse(line);
                    } catch (parseError) {
                        console.error(`❌ JSON parse error for line: "${line.substring(0, 100)}..."`);
                        continue;
                    }
                    
                    // Skip if old message or from us
                    if (message.id <= this.lastMessageId || message.is_from_me) {
                        continue;
                    }
                    
                    // New incoming message!
                    console.log(`📨 NEW MESSAGE [${message.id}]: "${message.text}"`);
                    this.processMessage(message);
                    
                    this.lastMessageId = message.id;
                    this.saveLastMessageId();
                }
                
            } catch (e) {
                console.error('❌ Error parsing messages:', e.message);
            }
        });
    }
    
    processMessage(message) {
        // Send typing indicator
        this.sendReply('🔍 Processing your message...');
        
        // Process through current OpenClaw session
        const escapedText = message.text.replace(/'/g, "'\"'\"'").replace(/\$/g, '\\$');
        const sessionCommand = `openclaw sessions send --message '${escapedText}' --session main`;
        
        exec(sessionCommand, { timeout: 30000 }, (error, stdout) => {
            let response = '';
            
            if (error) {
                console.error('❌ OpenClaw error:', error.message);
                response = 'Sorry, I encountered an error processing your message. Please try again.';
            } else {
                response = stdout.trim() || 'Message received but no response generated.';
            }
            
            // Remove the "processing" message and send real response
            setTimeout(() => {
                this.sendReply(response);
            }, 1000);
        });
    }
    
    sendReply(text) {
        const cleanText = text.replace(/"/g, '\\\\"').replace(/'/g, "'\"'\"'");
        const sendCommand = `imsg send --to "${this.phoneNumber}" --text "${cleanText}"`;
        
        exec(sendCommand, (error) => {
            if (error) {
                console.error('❌ Error sending reply:', error.message);
            } else {
                console.log(`✅ Sent: "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`);
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
            const state = { lastMessageId: this.lastMessageId, timestamp: Date.now() };
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
    console.log('\\n🛑 Shutting down...');
    process.exit(0);
});

// Start monitoring
const monitor = new SimpleMessageMonitor();
monitor.start();