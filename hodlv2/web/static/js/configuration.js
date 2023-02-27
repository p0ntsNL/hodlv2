$(document).ready(function() {

  $('.select2').select2({
    dropdownPosition: 'below'
  });

  $(".add-bot").click(function(e) {
    e.preventDefault();
    var x = Date.now();
    $(".bot-container").append('<div class="row"><div class="col-12"><span class="font-weight-bold">Bot #'+x+'</span></div><div class="mb-2 col-md-6"><label for="BotMarket" class="form-label">Market</label><input type="hidden" class="form-control market-hidden" name="Bot_'+x+'_Market_hidden"><select required class="form-control select2 market-dropdown" name="Bot_'+x+'_Market"></select><div class="exchange_response text-info"></div></div><div class="mb-2 col-md-6"><label for="BotSide" class="form-label">Side</label><select class="form-control" name="Bot_'+x+'_Side"><option selected="selected">buy</option><option>sell</option></select></div><div class="mb-2 col-md-6"><label for="BotTradeValue" class="form-label">Trade value</label><input required type="number" step="0.000001" min="0.000001" class="form-control" name="Bot_'+x+'_TradeValue_"></div><div class="mb-2 col-md-6"><label for="BotMaxTrades" class="form-label">Max trades</label><input required type="number" step="1" min="0" class="form-control" name="Bot_'+x+'_MaxTrades_"></div><div class="mb-2 col-md-6"><label for="BotPercOpen" class="form-label">Perc open</label><div class="input-group"><input required type="number" step="0.01" min="0.5" class="form-control" name="Bot_'+x+'_PercOpen"><div class="input-group-text">%</div></div></div><div class="mb-2 col-md-6"><label for="BotPercClose" class="form-label">Perc close</label><div class="input-group"><input required type="number" step="0.01" min="0.5" class="form-control" name="Bot_'+x+'_PercClose"><div class="input-group-text">%</div></div></div><div class="mb-2 col-md-6"><label for="BotTakeProfitIn" class="form-label">Take profit in</label><input type="hidden" class="form-control take-profit-in '+x+'-take-profit-in-hidden" name="Bot_'+x+'_TakeProfitIn_hidden"><select required class="form-control '+x+'-take-profit-in-dropdown" name="Bot_'+x+'_TakeProfitIn"></select></div><div class="mb-2 col-md-6"><label for="BotResetNextTradePrice" class="form-label">Reset next trade price</label><div class="input-group"><input required type="number" step="1" min="0" class="form-control" name="Bot_'+x+'_ResetNextTradePrice"><div class="input-group-text">day(s)</div></div></div><div class="col-12"><a type="button" href="#" class="btn btn-primary delete">Delete bot</a><hr></div></div>');
    updateMarkets();
  });

  $(".bot-container").on("click", ".delete", function(e) {
      e.preventDefault();
      $(this).parent('div').parent('div').remove();
  })

  $("#config").submit(function () {
  
    event.preventDefault();
    const myFormData = new FormData(event.target);
    const data = {};
    myFormData.forEach((value, key) => (data[key] = value));
  
    event.preventDefault()
    $.ajax({
      url: "/checkconfig",
      data: data,
      type: "POST",
      success: function (response) {
        if (response === "ok") {
          swal
            .fire({
              icon: "success",
              title: "Configuration saved.",
            })
            .then((result) => {
              window.location.reload();
            })
        } else {
          swal
            .fire({
              icon: "error",
              title: "Configuration not saved.",
              text: response,
            })
        }
      },
    })
  })

  function updateMarkets(clean=false) {
    if (clean == true) {
      $('.bot-container').empty();
    };
    var exchange = $('#exchange').val();
    if (exchange == undefined) {
      var exchange = 'kraken';
    };
    $('.exchange_response').html("Loading markets...");
    $.ajax({
       url: '/updatemarkets',
       type: 'post',
       data: {exchange: exchange},
       success: function(response){
         $('.market-dropdown').each(function() {
           let market_dropdown = $(this);
           market_dropdown.empty();
           var active_market = market_dropdown.prev('.market-hidden').val();
           var bot_id = market_dropdown.prev('.market-hidden').attr('name').split('_')[1];
           let takeprofitin_dropdown = $('.'+bot_id+'-take-profit-in-dropdown');
           var active_takeprofitin = takeprofitin_dropdown.prev('.'+bot_id+'-take-profit-in-hidden').val();
           var counter = 0;
           $.each(response, function (key, value) {
             if (active_market == value) {

               var base = value.split('/')[0];
               var quote = value.split('/')[1];

               takeprofitin_dropdown.empty();

               market_dropdown.append($('<option selected="selected"></option>').attr('value', value).text(value));

               if (active_takeprofitin == base) {
                 takeprofitin_dropdown.append($('<option selected="selected"></option>').attr('value', value.split('/')[0]).text(value.split('/')[0]));
               } else {
                 takeprofitin_dropdown.append($('<option></option>').attr('value', value.split('/')[0]).text(value.split('/')[0]));
               };
               if (active_takeprofitin == quote) {
                 takeprofitin_dropdown.append($('<option selected="selected"></option>').attr('value', value.split('/')[1]).text(value.split('/')[1]));
               } else {
                 takeprofitin_dropdown.append($('<option></option>').attr('value', value.split('/')[1]).text(value.split('/')[1]));
               };
             } else {
               market_dropdown.append($('<option></option>').attr('value', value).text(value));
               if (counter == 0) {
                 takeprofitin_dropdown.empty();
                 takeprofitin_dropdown.append($('<option></option>').attr('value', value.split('/')[0]).text(value.split('/')[0]));
                 takeprofitin_dropdown.append($('<option selected="selected"></option>').attr('value', value.split('/')[1]).text(value.split('/')[1]));
               };
             };
             counter++;
           })
         })
         $('.exchange_response').html("");
       }
    })
  }

  updateMarkets();
  $('#exchange').change(function(e){
    updateMarkets(clean=true);
  })

  $('body').on('change', '.market-dropdown', function() {
    let market_dropdown = $(this).closest('.row').find('.market-dropdown');
    var market = market_dropdown.val();
    var bot_id = market_dropdown.attr('name').split('_')[1];
    let takeprofitin_dropdown = $('.'+bot_id+'-take-profit-in-dropdown');
    takeprofitin_dropdown.empty();
    takeprofitin_dropdown.append($('<option></option>').attr('value', market.split('/')[0]).text(market.split('/')[0]));
    takeprofitin_dropdown.append($('<option selected="selected"></option>').attr('value', market.split('/')[1]).text(market.split('/')[1]));
  });

})
