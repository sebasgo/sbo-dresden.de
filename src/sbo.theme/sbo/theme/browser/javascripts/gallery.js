jq(document).ready(function()
{
    var slideShow = null;
    
    var createSlideShow = function()
    {
        slideShow = {};
        slideShow.imgUrls = [];
        slideShow.imgTitles = [];
        
        jq('#content div.gallery a').each(function()
        {
            slideShow.imgUrls.push(jq(this).attr('href'));
            slideShow.imgTitles.push(jq(this).attr('title'));
        });
        
        jq('body').append('<div id="slideshow"></div>');
        slideShow.elem = jq('#slideshow');
        
        slideShow.elem.append('<div class="bg"></div>');
        slideShow.elem.append(
            '<div class="title">'
            + '<a class="close_btn" href="#"></a>'
            + '<span class="title_label"></span>'
            + '</div>'
        );
        slideShow.elem.append(
            '<div class="bottombar">'
            + '<span class="img_index"></span>'
            + '&nbsp;'
            + '<span class="img_title"></span>'
            + '</div>'
        );
        slideShow.elem.append(
            '<div class="controls">'
            + '<div class="left"></div>'
            + '<div class="right"></div>'
            + '</div>'
        );
        
        slideShow.elem.find('.title_label').text(
            jq('#content .documentFirstHeading').text()
        );
        slideShow.elem.children('.bg').css('opacity', 0.9);
        slideShow.elem.find('.controls').children('div').css('opacity', 0.0);
        
        slideShow.elem.find('.close_btn').click(function(event)
        {
            event.preventDefault();
            hide();
        });
        slideShow.elem.find('.controls .left').click(previousImg);
        slideShow.elem.find('.controls .right').click(nextImg);
        
        slideShow.imgIndex = 0;
    };
    
    var loadImg = function(imgIndex, callback)
    {
        var imgLoaded = function()
        {
            slideShow.elem.children('img').addClass('old').stop(true, true);
            slideShow.elem.children('img').fadeOut(500, function()
            {
                slideShow.elem.children('img.old').remove();
            });
            jq(img).appendTo(slideShow.elem);
            alignImage();
            jq(img).fadeIn(500);
            callback();
        }
        
        var img = document.createElement("img");
        jq(img).bind("load", imgLoaded);
        slideShow.imgIndex = imgIndex;
        slideShow.elem.find('.img_title').text(
                slideShow.imgTitles[imgIndex]
        );
        slideShow.elem.find('.img_index').text(
            (imgIndex + 1) + "/" + slideShow.imgUrls.length + ":"
        );
        img.src = slideShow.imgUrls[imgIndex] + "/image_large";
    };
    
    var preloadImg = function(imgIndex)
    {
        var preloader = document.createElement('img');
        
        jq(preloader).bind("load", function()
        {
            preloader = null;
        });
        
        preloader.src = slideShow.imgUrls[imgIndex] + "/image_large";
    };
    
    var nextImg = function()
    {
        var imgCount = slideShow.imgUrls.length;
        var index = slideShow.imgIndex;
        loadImg((index + 1) % imgCount, function()
        {
            preloadImg((index + 2) % imgCount);
        });
    };
    
    var previousImg = function()
    {
        var imgCount = slideShow.imgUrls.length;
        var index = slideShow.imgIndex;
        loadImg((index + imgCount - 1) % imgCount, function()
        {
            preloadImg((index + imgCount - 2) % imgCount);
        });
    };
    
    var updateGeometry = function()
    {
        slideShow.elem.css({
            top: jq(window).scrollTop(),
            left: jq(window).scrollLeft(),
            width: jq(window).width(),
            height: jq(window).height()
        });
        slideShow.elem.children(".bg").css({
            width: jq(window).width(),
            height: jq(window).height()
        });
        slideShow.elem.children(".title").css({
            width: jq(window).width()
                - parseInt(slideShow.elem.find(".title").css('paddingLeft'))
                - parseInt(slideShow.elem.find(".title").css('paddingRight'))
        });
        slideShow.elem.children(".bottombar").css({
            top: jq(window).height() 
                - slideShow.elem.children(".bottombar").outerHeight(),
            width: jq(window).width()
                - parseInt(slideShow.elem.find(".bottombar").css('paddingLeft'))
                - parseInt(slideShow.elem.find(".bottombar").css('paddingRight'))
        });
        slideShow.elem.children('.controls').css({
            top: slideShow.elem.children('.title').outerHeight(),
            width: jq(window).width(),
            height: jq(window).height()
                - slideShow.elem.children('.title').outerHeight()
                - slideShow.elem.children('.bottombar').outerHeight()
        });
        slideShow.elem.find('.controls .left').css({
            width: parseInt(jq(window).width() / 2),
            height: slideShow.elem.children('.controls').height()
        });
        slideShow.elem.find('.controls .right').css({
            left: slideShow.elem.find('.controls .left').outerWidth(),
            width: jq(window).width()
                - slideShow.elem.find('.controls .left').outerWidth(),
            height: slideShow.elem.children('.controls').height()
        });
        slideShow.elem.find('.controls div').bind({
            mouseenter: function(event)
            {
                jq(event.target).stop(true).animate({
                    'opacity': 0.5
                });
            },
            mouseleave: function(event)
            {
                jq(event.target).stop(true).animate({
                    'opacity': 0.0
                });
            }
        });
        
        alignImage();
    };
    
    var show = function()
    {
        if (!slideShow)
        {
            createSlideShow();
        }
        
        jq('body').css('overflow', "hidden");
        slideShow.elem.css({
            display: 'block'
        });
        updateGeometry();
        jq(window).bind('scroll resize', updateGeometry);
        jq(document).bind('keyup', handleKeyPress);
    };
    
    var hide = function()
    {
        jq(window).unbind('scroll resize', updateGeometry);
        jq(document).unbind('keyup', handleKeyPress);
        slideShow.elem.css({
            display: 'none'
        });
        jq('body').css('overflow', "auto");
        slideShow.elem.children('img').remove();
    };
    
    var alignImage = function()
    {
        slideShow.elem.children('img').each(function()
        {
            jq(this).css({
                top: parseInt((jq(window).height() - jq(this).outerHeight()) / 2),
                left: parseInt((jq(window).width() - jq(this).outerWidth()) / 2)
            });
        });
    };
    
    var handleKeyPress = function(event)
    {
        switch(event.which)
        {
            case 37:
                event.preventDefault();
                previousImg();
                break;
            case 39:
                event.preventDefault();
                nextImg();
                break;
            case 27:
                event.preventDefault();
                hide();
                break;
        }
    }
    
    jq('#content div.gallery a').click(function(event)
    {
        event.preventDefault();
        show();
        
        var imgUrl = jq(event.target.parentNode).attr('href');
        var imgCount = slideShow.imgUrls.length;

        for (var index = 0; index < imgCount; index++)
        {
            if (slideShow.imgUrls[index] == imgUrl)
            {
                break;
            }
        }
        
        loadImg(index, function()
        {
            preloadImg((index + 1) % imgCount);
            preloadImg((index + imgCount - 1) % imgCount);
        });
    });
    
});
