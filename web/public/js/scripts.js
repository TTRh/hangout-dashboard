// sparkline generator with xscale information
function sparkline_xscale(selector,formater) {
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
    tooltipFormat: '<span style="color: {{color}}">&#9679;</span> {{prefix}}{{y}} at {{x:label}}{{suffix}}</span>',
    tooltipValueLookups: {
      label: $.range_map(xscale)
    }
  });
}

// init sparklines HH:MM by 10 minutes step
sparkline_xscale('.sparkline.xscale-hm',function(k){
    return k.substr(0,2) + "h" + k.substr(2);
  }
);

// init sparklines dd/mm/YYYY
sparkline_xscale('.sparkline.xscale-ymd',function(k){
    return k.substr(6) + "/" + k.substr(4,2) + "/" + k.substr(0,4);
  }
);

// init sparklines mm/YYYY
sparkline_xscale('.sparkline.xscale-ym',function(k){
    return k.substr(4) + "/" + k.substr(0,4);
  }
);

// init boostrap tooltip
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

// animate progress bar on page load
var callback = function(){
	$('.item-skills').each(function(){
		newWidth = $(this).parent().width() * $(this).data('percent');
		$(this).width(0);
    $(this).animate({
        width: newWidth,
    }, 1000);
	});
};
$(document).ready(callback);

// animate progress bar on resize bar
var resize;
window.onresize = function() {
	clearTimeout(resize);
	resize = setTimeout(function(){
		callback();
	}, 100);
};
