const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: process.env.NODE_ENV !== 'production',
  productionSourceMap: false,
  configureWebpack: {
    performance: {
      hints: false
    }
  }
}) 