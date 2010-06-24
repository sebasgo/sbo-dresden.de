jq(document).ready(function() {
    setupContentMenu();
    setupHandlers();
    setupNavigation();
});

setupContentMenu = function() {
}

setupHandlers = function() {
    var $ = jq;
  
    // setup collapsing blocks
    $.each($("div.expandable-section, a.expandable-label"), function(i, o) {
		$(o).bind('click', function() {
		    var section = $(o).parent();
		    var content = $("div.expandable-content", section);
		    var container = section.parents('.collage-row').eq(0);
		    var url = $(o).attr('href');
		    
		    // case content type dropdown, click event is bound here too
		    if(!url) {
		    	return;
		    }
			    
		    if ($(o).attr('class').indexOf('enabled') != -1) {
				// disable
				content.css('display', 'none');
				container.next('.collage-row').eq(0).css('margin-top',
				                                         0 + 'px');
		    } else {
			    // enable
				content.css('display', 'block');
		
				// handle height (for IE6)
				container.next('.collage-row').eq(0).css('margin-top',
				                                         1 + 'px');
				
				// handle ajax sections
				$.each($(".expandable-ajax-content", section), function(j, p) {
				    $(p).load(url, function() {
						container.next('.collage-row').eq(0).css('margin-top',
						                                         1 + '%');
						setupExistingItemsForm();
				    });
				});
		    }
		    
		    $(o).toggleClass('enabled').blur();
		    return false;
		});
    });
}

setupNavigation = function() {
    var $ = jq;
  
    // transform navigation links into ajax-methods
    $("a.collage-js-down").bind('click', {jquery: $}, triggerMoveDown);
    $("a.collage-js-up").bind('click', {jquery: $}, triggerMoveUp);
}

submitExistingItemsForm = function(formel) {
    var $ = jq;  
	// serialize form
	var form = $(formel).parents('form').eq(0);
	var url = form.attr('action');
	var inputs = $(':input', form);

	// refresh form
	var section = $(formel).parents('.expandable-ajax-content').eq(0);
	section.load(url, extractParams(inputs.serialize()), function() {
		setupExistingItemsForm();
	});
}

setupExistingItemsForm = function() {
    var $ = jq;
    
    $("form.collage-existing-items select").change(function(event) {
		this.blur();
        submitExistingItemsForm(this);
    });
    // $("form.collage-existing-items SearchableText");
    $("form.collage-existing-items [@name=SearchableText]").keydown(function(e) {
	    if (e.keyCode == 13) { // ESC
		    e.preventDefault;
			submitExistingItemsForm(this);
		}
	});
}

postMessage = function(element, msg) {
    element._contents = element.innerHTML;
    element.innerHTML += ' (' + msg + ')';
}

restoreElement = function(element) {
    element.innerHTML = element._contents;
}

doSimpleQuery = function(url, data) {
    var $ = jq;
    
    // perform simple ajax-call
    var href = url.split('?');
    var url = href[0];
    data = (href.length > 1) ? extractParams(href[1]) : {};
	
    // avoid aggresive IE caching
    data['url'] = (new Date()).getTime();

    // set simple flag
    data['simple'] = 1
    
    // display a save message
    var heading = $('h1.documentFirstHeading').get(0);
    if (heading) postMessage(heading, 'Saving...');

    $.post(url, data, function(data) {
	    if (heading) restoreElement(heading);
    });
}

extractParams = function(query) {
    // convert a query-string into a dictionary
    var data = {};
    var params = query.split('&');
    for (var i=0; i<params.length; i++) {
		var pair = params[i].split('=');
		data[pair[0]] = pair[1];
    }

    return data;
}

triggerMoveDown = function(event) {
    return triggerMove.call(this, event, +1);
}

triggerMoveUp = function(event) {
    return triggerMove.call(this, event, -1);
}

triggerMove = function(event, direction) {
    var $ = jq;
    
    $ = event.data.jquery;
    event.preventDefault();

    var link = $(this);
    link.blur();
    
    var className = event.data.className;
    
    var row = link.parents('.collage-row').eq(0);
    var column = link.parents('.collage-column').eq(0);
    var item = link.parents('.collage-item').eq(0);

    var destination = null;
    var origin = null;
    var items = null;

    if (item.length) {
		items = $('.collage-item', column);
		origin = $(item);
    } else if (column.length) {
		items = $('.collage-column', row);
		origin = $(column);
    } else {
		items = $('.collage-row');
		origin = $(row);
    }

    var index = items.index(origin.get(0));
    if (!(index+direction >= 0 && index+direction < items.length)) return false;
    
    destination = $(items[index+direction]);
    swap(origin, destination);

    doSimpleQuery(link.attr('href'));    
}

swap = function(origin, destination) {
    var temp = origin.after('<span></span>').next();
    destination.after(origin);
    destination.insertBefore(temp);
    temp.remove();
}
