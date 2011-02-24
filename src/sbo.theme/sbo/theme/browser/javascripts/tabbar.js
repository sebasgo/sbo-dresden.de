$(document).ready(function()
{
    var animateTabbar = function(tabbar)
    {
        var time = 250;
        
        var selectedTab = tabbar.children("li.selected").get(0);
        var activeTab = selectedTab;
        var tabs = tabbar.children("li");
        var resetTimer = 0;
        
        tabs.removeClass("selected plain");
        tabbar.append('<div class="marker"></div>')
        
        var marker = tabbar.children(".marker");
        
        marker.append('<div class="left-edge"></div>');
        marker.append('<div class="right-edge"></div>');
        
        if (activeTab)
        {
            $(activeTab).addClass("active");
            marker.css("left", activeTab.offsetLeft);
            marker.css("width", activeTab.offsetWidth);
            $(activeTab).children("ul").css("display", "block");
        }
        
        var goToTab = function(target)
        {
            if (activeTab == target)
            {
                return;
            }
            
            var sub = $(target).children("ul").get(0);
            var oldSub = $(activeTab).children("ul").get(0);
            
            var slideOutDir = "up";
            var slideInDir = "up";
            
            if (sub && oldSub)
            {
                var diff = tabs.index(target) - tabs.index(activeTab);
                slideOutDir = diff > 0? "left": "right";
                slideInDir = diff < 0? "left": "right";
            }
            
            
            $(oldSub).css("display", "none");
            $(oldSub).hide("slide", {direction: slideOutDir}, time);
            $(activeTab).removeClass("active");
            
            activeTab = target;
            
            if (activeTab)
            {
                marker.animate({
                    left: activeTab.offsetLeft,
                    width: activeTab.offsetWidth
                }, time, "linear", function()
                {
                    if (target == activeTab)
                    {
                        $(target).addClass("active");
                    }
                });
                $(sub).show("slide", {direction: slideInDir}, time);
            }
            else
            {
                marker.animate({
                    left: 0,
                    width: 0
                }, time, "linear");
            }
        }
        
        tabs.mouseover(function(event)
        {
            goToTab(event.currentTarget);
        });
        
        tabbar.mouseleave(function()
        {
            resetTimer = setTimeout(function()
            {
                goToTab(selectedTab);
            }, 1000);
        });
        
        tabbar.mouseenter(function()
        {
            clearTimeout(resetTimer);
        });
    };
    
    var tabbar = $("#portal-globalnav");
    
    animateTabbar(tabbar);
    
    tabbar.find("ul.level-two").each(function(index, elem)
    {
        animateTabbar($(elem));
    });
     
});
