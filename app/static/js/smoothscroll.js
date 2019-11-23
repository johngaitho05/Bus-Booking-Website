var scrollLink = $('.scroll');

scrollLink.click(function(e){

    e.preventDefault();

    $('body,html').animate({

        scrollTop: $(this.hash).offset().top-50

    },1000);
    $('.active').removeClass('active');
    $(this).parent().addClass('active');

});
