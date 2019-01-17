const functions = require('firebase-functions')
const express = require('express')
const utils = require('./utils')

const selectJson = utils.jsonLoad(__dirname + '/db/select.json')
const dataJson = utils.jsonLoad(__dirname + '/db/data.json')


const app = express()
app.get('/api/select', (request, response) => {
  response.send(selectJson)
})

app.get('/api/search', (request, response) => {
  const updated_at = dataJson['updated_at']
  const search_params = [
    [0, 'title'],
    [0, 'folder'],
    [2, 'name'],
    [1, 'editors'],
    [2, 'overview'],
  ]

  // 絞り込み前の全データ
  let temp_data = dataJson['result']
  search_params.forEach((p) => {
    let pattern = p[0]
    let param = p[1]
    const q = request.query[param]

    if (q === undefined) {
      return false
    }

    let checker = null
    if (pattern === 0) {
      checker = function (x) {
        return new RegExp(q).test(x[param]['value'])
      }
    } else if (pattern === 1) {
      checker = function (x) {
        return new RegExp(q).test(x[param].join(','))
      }
    } else {
      checker = function (x) {
        return new RegExp(q).test(x[param])
      }
    }

    temp_data = temp_data.filter(checker)
  })

  let page = request.query.page
  let page_limit = 0
  let page_result = []
  if (page !== undefined && page !== '0') {
    page = parseInt(page)

    // ページのカラム数
    const page_cols = 10

    const index = page - 1
    page_result = temp_data.slice(index*page_cols, index*page_cols+10)

    page_limit = Math.ceil(temp_data.length / page_cols)
    if (page_limit === 0) {
      page_limit = 1
    }
  }

  const result = {
    page: page,
    page_limit: page_limit,
    result: page_result,
    updated_at: updated_at
  }

  response.send(result)
})

exports.app = functions.https.onRequest(app);
