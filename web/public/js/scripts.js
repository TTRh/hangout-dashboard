/***************************************
 * sparkline
 ***************************************/

// sparkline generator with xscale information
function sparkline_xscale(type,selector,formater) {
  var sparkline = $(selector);
  var data = JSON.parse(sparkline.html());
  var xscale = data.reduce(function(x,y,i){
    var item = {};
    item[i] = formater(y[0]);
    return $.extend(x,item)
  },{});
  var values = data.map(function(x){return x[1]});
  sparkline.sparkline(values, {
    type: 'line',
    width: '100%',
    height: '38px',
    lineColor: '#1a0dab',
    spotColor: '#FFFFFF',
    minSpotColor: '#DA4336',
    maxSpotColor: '#10a461',
    highlightSpotColor: '#1a0dab',
    tooltipFormat: '<span style="color: {{color}}">&#9679;</span> {{prefix}}{{x:label}} : {{y}}{{suffix}}</span>',
    tooltipValueLookups: {
      label: $.range_map(xscale)
    }
  });
}

function update_sparkline() {
  // init sparklines HH:MM by 10 minutes step
  sparkline_xscale('line','.sparkline.xscale-hm',function(k){
      return k.substr(0,2) + "h" + k.substr(2);
    }
  );
  // init sparklines dow
  sparkline_xscale('bar','.sparkline.xscale-dow',function(k){
      dow = { "0": "Monday", "1": "Tuesday", "2": "Wednesday", "3": "Thursday", "4": "Friday", "5": "Saturday", "6": "Sunday" }
      return dow[k]
    }
  );
  // init sparklines dd/mm/YYYY
  sparkline_xscale('line','.sparkline.xscale-ymd',function(k){
      return k.substr(6) + "/" + k.substr(4,2) + "/" + k.substr(0,4);
    }
  );
  // init sparklines mm/YYYY
  sparkline_xscale('bar','.sparkline.xscale-ym',function(k){
      return k.substr(4) + "/" + k.substr(0,4);
    }
  );
}

/***************************************
 * bootstrap initialization
 ***************************************/

// init boostrap tooltip
function update_tooltip() {
  $('[data-toggle="tooltip"]').tooltip()
}

/***************************************
 * progress bar animation on load page
 ***************************************/

// animate progress bar on page load
function update_progress_bar() {
	$('.item-skills').each(function(){
		newWidth = $(this).parent().width() * $(this).data('percent');
		$(this).width(0);
    $(this).animate({
        width: newWidth,
    }, 1000);
	});
}

/***************************************
 * init function
 ***************************************/

var init_on_load = function () {
  update_tooltip();
  update_sparkline();
  update_progress_bar();
};

$(document).ready(init_on_load);

/***************************************
 * document resize
 ***************************************/

var reload_on_resize = function() {
  update_progress_bar();
};

// animate progress bar on resize bar
var resize;
window.onresize = function() {
	clearTimeout(resize);
	resize = setTimeout(function(){
		reload_on_resize();
	}, 100);
};
