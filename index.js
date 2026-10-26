const mineflayer = require('mineflayer')

function createBot() {
  const bot = mineflayer.createBot({
    host: process.env.smp || 'razesmp.progamer.me', // Render ke environment variable se IP uthayega
    port: 25565,                            // Y apna exact Port number dalein (agar 25565 nahi hai toh)
    username: 'AFK_Guardian'
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