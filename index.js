const mineflayer = require('mineflayer')
const http = require('http')

// 1. Render HTTP Server
const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' })
  res.end('AFK Bot is running 24/7!\n')
})

const PORT = process.env.PORT || 3000
server.listen(PORT, () => {
  console.log(`Web server is listening on port ${PORT}`)
})

// 2. Minecraft Bot Setup (version: false se ye automatically server ka version pakad lega)
function createBot() {
  const bot = mineflayer.createBot({
    host: process.env.smp || 'razesmp.progamer.me', 
    port: 25565,                            
    username: 'AFK_Guardian',
    version: false // <-- Yeh sabse important fix hai (Auto-detect version)
  })

  bot.on('spawn', () => {
    console.log('Bot successfully server me enter ho gaya hai!')

    setInterval(() => {
      const yaw = Math.random() * Math.PI * 2
      const pitch = (Math.random() * Math.PI) - (Math.PI / 2)
      bot.look(yaw, pitch, true)
    }, 60000) 
  })

  bot.on('kicked', (reason) => {
    console.log(`Bot kick ho gaya: ${reason}`)
    attemptReconnect()
  })

  bot.on('error', (err) => {
    console.log('Error aaya:', err)
  })

  bot.on('end', () => {
    console.log('Connection toot gaya, reconnect kar rahe hain...')
    attemptReconnect()
  })
}

function attemptReconnect() {
  setTimeout(() => {
    console.log('Dubara connect hone ki koshish...')
    createBot()
  }, 10000)
}

createBot()
