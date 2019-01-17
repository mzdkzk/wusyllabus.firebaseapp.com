const fs = require('fs')

exports.jsonLoad = (filename, options='utf8') => {
  return JSON.parse(fs.readFileSync(filename, options))
}
