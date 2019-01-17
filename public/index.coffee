API_BASE_URL = '/api'
API_URL1 = API_BASE_URL + '/select'
API_URL2 = API_BASE_URL + '/search'

api1_result = null
page = 1
page_limit = 1

$ ->
# 読み込み時に選択肢情報を取得
  $.get API_URL1, (response) ->
# ローカルに保存
    api1_result = response

    $('#updated_at').text(response.updated_at)

    $('#title').empty()
    $('#title').append "<option value='0'>選択して下さい</option>"

    for result in response.result
      $('#title').append "<option value='#{result.value}'>#{result.name}</option>"

  $('#title').on 'change', ->
    $('#folder').empty()
    $('#folder').append "<option value='0'>選択して下さい</option>"
    if $('#title').val() == '0'
      return

    for result in api1_result.result
      if result.value == $('#title').val()
        for folder in result.folders
          $('#folder').append "<option value='#{folder.value}'>#{folder.name}</option>"
    return

  $('#submit').on 'click', ->
    if is_searching
      return

    if 'return' in $(this).attr('class').split ' '
      $('#result').empty()
      $('.pagenation-menu').hide()
      $('.form-group').show()
      $('#submit').text('検索').removeClass 'return'
      page = 1
      $('#now-page').text page
      $('#page-limit').text page
      return

    search()
    $('.pagenation-menu').show()
    $('#submit').text('戻る').addClass 'return'

is_searching = false

search = ->
  is_searching = true
  $('.loading').show()

  param = {}
  for i in $('.search-input')
    param[i.id] = $(i).val()

  if param.title == '0'
    delete param.title
  if param.folder == '0'
    delete param.folder
  param['page'] = page

  $.get API_URL2, param, (response) ->
    $('.form-group').hide()
    $('#result').empty()

    for result, i in response.result
      editors = result.editors[0]
      if result.editors.length > 1
        editors += ' 他'
      td = """
           <tr id='#{i}'>
             <td><a href="#{result.page_url}" target="_blank">#{result.name}</a></td>
             <td>#{editors}</td>
             <td>#{result.semester}</td>
             <td>#{result.period}</td>
           </tr>
           """
      $('#result').append td

    if response.result.length == 0
      $('#result').append "<p>結果無し</p>"

    $('#now-page').text response.page
    page_limit = response.page_limit
    $('#page-limit').text page_limit

    $('.loading').hide()
    is_searching = false
    return
  return

$('#next').on 'click', ->
  if is_searching or page >= page_limit
    return
  page += 1
  search()
  return

$('#prev').on 'click', ->
  if is_searching or page == 1
    return
  page -= 1
  search()
  return
