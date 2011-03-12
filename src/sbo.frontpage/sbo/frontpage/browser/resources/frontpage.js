$(document).ready(function()
{
    var setupNewsBox = function()
    {
        var navTimeout = 0;        
        var newsBox = $("#content-core .news");
        
        var navigate = function(switchForward)
        {
            var currentPane = newsBox.children(".pane.active").get(0);
            $(currentPane).fadeOut(500, function()
            {
                $(currentPane).removeClass("active");
            });
            
            nextPane = switchForward?
                $(currentPane).next(".pane").get(0):
                $(currentPane).prev(".pane").get(0);
            
            if (!nextPane)
            {
                nextPane = switchForward?
                    newsBox.children(".pane").first().get(0):
                    newsBox.children(".pane").last().get(0);
            }
            
            $(nextPane).fadeIn(500, function()
            {
                $(nextPane).addClass("active");
            });
            
            setupTimer();
        }
        
        var createNavigationButtons = function()
        {
            var createButton = function(which)
            {
                newsBox.append(
                    '<a href="#" class="navbutton ' + which + '"><!-- --></a>'
                );
                
                newsBox.children("a." + which).click(function(event)
                {
                    event.preventDefault();
                    navigate(which == "next");
                });
            };
            
            createButton("next");
            createButton("previous");
            
            newsBox.mouseenter(function()
            {
                newsBox.children("a.navbutton").fadeIn(250);
            });
            
            newsBox.mouseleave(function()
            {
                newsBox.children("a.navbutton").fadeOut(250);
            });
        };
        
        var setupTimer = function()
        {
            clearTimeout(navTimeout);
            navTimeout = setTimeout(function()
            {
                navigate(true);
            }, 5000);
        };
        
        createNavigationButtons();
        setupTimer();
    };
    
    if($("body.portaltype-frontpage").get(0))
    {
        setupNewsBox();
    }
});

