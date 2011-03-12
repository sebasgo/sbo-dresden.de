$(document).ready(function()
{
    var setupNewsBox = function()
    {
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
                $(currentPane).previous(".pane").get(0);
            
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
        }
        
        setInterval(function()
        {
            navigate(true);
        }, 5000);
    };
    
    if($("body.portaltype-frontpage").get(0))
    {
        setupNewsBox();
    }
});

