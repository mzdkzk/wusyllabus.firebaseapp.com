// Generated by CoffeeScript 2.3.2
(function() {
  var API_BASE_URL, API_URL1, API_URL2, api1_result, is_searching, page, page_limit, search,
    indexOf = [].indexOf;

  API_BASE_URL = '/api';

  API_URL1 = API_BASE_URL + '/select';

  API_URL2 = API_BASE_URL + '/search';

  api1_result = null;

  page = 1;

  page_limit = 1;

  $(function() {
    // 読み込み時に選択肢情報を取得
    $.get(API_URL1, function(response) {
      var j, len, ref, result, results;
      // ローカルに保存
      api1_result = response;
      $('#updated_at').text(response.updated_at);
      $('#title').empty();
      $('#title').append("<option value='0'>選択して下さい</option>");
      ref = response.result;
      results = [];
      for (j = 0, len = ref.length; j < len; j++) {
        result = ref[j];
        results.push($('#title').append(`<option value='${result.value}'>${result.name}</option>`));
      }
      return results;
    });
    $('#title').on('change', function() {
      var folder, j, k, len, len1, ref, ref1, result;
      $('#folder').empty();
      $('#folder').append("<option value='0'>選択して下さい</option>");
      if ($('#title').val() === '0') {
        return;
      }
      ref = api1_result.result;
      for (j = 0, len = ref.length; j < len; j++) {
        result = ref[j];
        if (result.value === $('#title').val()) {
          ref1 = result.folders;
          for (k = 0, len1 = ref1.length; k < len1; k++) {
            folder = ref1[k];
            $('#folder').append(`<option value='${folder.value}'>${folder.name}</option>`);
          }
        }
      }
    });
    return $('#submit').on('click', function() {
      if (is_searching) {
        return;
      }
      if (indexOf.call($(this).attr('class').split(' '), 'return') >= 0) {
        $('#result').empty();
        $('.pagenation-menu').hide();
        $('.form-group').show();
        $('#submit').text('検索').removeClass('return');
        page = 1;
        $('#now-page').text(page);
        $('#page-limit').text(page);
        return;
      }
      search();
      $('.pagenation-menu').show();
      return $('#submit').text('戻る').addClass('return');
    });
  });

  is_searching = false;

  search = function() {
    var i, j, len, param, ref;
    is_searching = true;
    $('.loading').show();
    param = {};
    ref = $('.search-input');
    for (j = 0, len = ref.length; j < len; j++) {
      i = ref[j];
      param[i.id] = $(i).val();
    }
    if (param.title === '0') {
      delete param.title;
    }
    if (param.folder === '0') {
      delete param.folder;
    }
    param['page'] = page;
    $.get(API_URL2, param, function(response) {
      var editors, k, len1, ref1, result, td;
      $('.form-group').hide();
      $('#result').empty();
      ref1 = response.result;
      for (i = k = 0, len1 = ref1.length; k < len1; i = ++k) {
        result = ref1[i];
        editors = result.editors[0];
        if (result.editors.length > 1) {
          editors += ' 他';
        }
        td = `<tr id='${i}'>\n  <td><a href="${result.page_url}" target="_blank">${result.name}</a></td>\n  <td>${editors}</td>\n  <td>${result.semester}</td>\n  <td>${result.period}</td>\n</tr>`;
        $('#result').append(td);
      }
      if (response.result.length === 0) {
        $('#result').append("<p>結果無し</p>");
      }
      $('#now-page').text(response.page);
      page_limit = response.page_limit;
      $('#page-limit').text(page_limit);
      $('.loading').hide();
      is_searching = false;
    });
  };

  $('#next').on('click', function() {
    if (is_searching || page >= page_limit) {
      return;
    }
    page += 1;
    search();
  });

  $('#prev').on('click', function() {
    if (is_searching || page === 1) {
      return;
    }
    page -= 1;
    search();
  });

}).call(this);
