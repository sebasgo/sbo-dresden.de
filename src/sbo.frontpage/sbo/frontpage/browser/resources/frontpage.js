jq(document).ready(function()
{
    var setupNewsBox = function()
    {
        var navTimeout = 0;        
        var newsBox = jq("#content-core .news");
        
        var navigate = function(switchForward)
        {
            var currentPane = newsBox.children(".pane.active").get(0);
            
            var hide = function()
            {
                jq(currentPane).hide(
                    "slide",
                    {
                        direction: switchForward? "left": "right"
                    },
                    500, 
                    function()
                    {
                        jq(currentPane).removeClass("active");
                    }
                );
            }
            
            var show = function()
            {
            jq(nextPane).show(
                "slide",
                {
                    direction: switchForward? "right": "left"
                },
                500, 
                function()
                {
                    jq(nextPane).addClass("active");
                }
            );
            }
            
            
            var nextPane = switchForward?
                jq(currentPane).next(".pane").get(0):
                jq(currentPane).prev(".pane").get(0);
            
            if (!nextPane)
            {
                nextPane = switchForward?
                    newsBox.children(".pane").first().get(0):
                    newsBox.children(".pane").last().get(0);
            }
            
            if (switchForward)
            {
                show();
                hide();
            }
            else
            {
                hide();
                show();
            }
            
            setupTimer();
        }
        
        var createNavigationButtons = function()
        {
            var createButton = function(which)
            {
                newsBox.append(
                    '<a href="#" class="navbutton ' + which + '"><!-- --></a>'
                );
                
                var button = newsBox.children("a." + which);
                
                button.css("opacity", 0);
                
                button.click(function(event)
                {
                    event.preventDefault();
                    navigate(which == "next");
                });
                
                button.mouseenter(function(event)
                {
                    button.stop().show().animate({
                        opacity: 0.8
                    }, 250);
                });
                
                button.mouseleave(function(event)
                {
                    button.stop().animate({
                        opacity: 0.5
                    }, 250);
                });
            };
            
            createButton("next");
            createButton("previous");
            
            newsBox.mouseenter(function()
            {
                newsBox.children("a.navbutton").stop().show().animate({
                    opacity: 0.5
                }, 250);
            });
            
            newsBox.mouseleave(function()
            {
                newsBox.children("a.navbutton").stop().fadeOut(250);
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
    
    if(jq("body.portaltype-frontpage").get(0))
    {
        setupNewsBox();
    }
});

