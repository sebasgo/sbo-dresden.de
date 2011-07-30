jq(document).ready(function()
{
    var animateTabbar = function(tabbar)
    {
        var time = 250;

        var selectedTab = tabbar.children("li.selected").get(0);
        var activeTab = selectedTab;
        var tabs = tabbar.children("li");
        var resetTimer = 0;
        var activateTimer = 0;
        var tabToActivate = null;
    
        tabs.removeClass("selected plain");
        tabbar.append('<div class="marker"></div>')
    
        var marker = tabbar.children(".marker");
    
        marker.append('<div class="left-edge"></div>');
        marker.append('<div class="right-edge"></div>');
    
        if (activeTab)
        {
            jq(activeTab).addClass("active");
            marker.css("left", activeTab.offsetLeft);
            marker.css("width", activeTab.offsetWidth);
            jq(activeTab).children("ul").css("display", "block");
        }
    
        var goToTab = function(target)
        {
            if (activeTab == target)
            {
                return;
            }
    
            var sub = jq(target).children("ul").get(0);
            var oldSub = jq(activeTab).children("ul").get(0);
        
            var slideOutDir = "up";
            var slideInDir = "up";
        
            if (sub && oldSub)
            {
                var diff = tabs.index(target) - tabs.index(activeTab);
                slideOutDir = diff > 0? "left": "right";
                slideInDir = diff < 0? "left": "right";
            }
            
            jq(oldSub).css("display", "none");
            jq(oldSub).hide("slide", {direction: slideOutDir}, time);
            jq(activeTab).removeClass("active");
        
            activeTab = target;
        
            if (activeTab)
            {
                marker.stop().animate({
                    left: activeTab.offsetLeft,
                    width: activeTab.offsetWidth
                }, time, "linear", function()
                {
                    if (target == activeTab)
                    {
                        jq(target).addClass("active");
                    }
                });
                jq(sub).show("slide", {direction: slideInDir}, time, function()
                {
                    if (target != activeTab)
                    {
                        jq(sub).css("display", "");
                    }
                });
            }
            else
            {
                marker.animate({
                    left: 0,
                    width: 0
                }, time, "linear");
            }
        }

        tabs.children("a").mouseover(function(event)
        {
            var tab = event.currentTarget.parentNode
            
            clearTimeout(activateTimer);
            tabToActivate = tab;
            
            activateTimer = setTimeout(function()
            {
                if (tabToActivate == tab)
                {
                    goToTab(tab);
                }
            }, 300);
        }).mouseout(function(event)
        {
            tabToActivate = null;
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

    if (jq.browser.msie)
    {
        if (parseInt(jq.browser.version, 10) < 7)
        {
            return;
        }
    }

    var tabbar = jq("#portal-globalnav");

    animateTabbar(tabbar);

    tabbar.find("ul.level-two").each(function(index, elem)
    {
        animateTabbar(jq(elem));
    });

});
