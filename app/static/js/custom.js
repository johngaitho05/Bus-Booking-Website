(function ($) {

    "use strict";

    // PRE LOADER
    $(window).load(function(){
        $('.preloader').fadeOut(1000); // set duration in brackets
    });


    // MENU
    $('.navbar-collapse a').on('click',function(){
        $(".navbar-collapse").collapse('hide');
    });

    $(window).scroll(function() {
        if ($(".navbar").offset().top > 50) {
            $(".navbar-fixed-top").addClass("top-nav-collapse");
        } else {
            $(".navbar-fixed-top").removeClass("top-nav-collapse");
        }
    });


    // PARALLAX EFFECT
    $.stellar({
        horizontalScrolling: false,
    });


    // MAGNIFIC POPUP
    $('.image-popup').magnificPopup({
        type: 'image',
        removalDelay: 300,
        mainClass: 'mfp-with-zoom',
        gallery:{
            enabled:true
        },
        zoom: {
            enabled: true, // By default it's false, so don't forget to enable it

            duration: 300, // duration of the effect, in milliseconds
            easing: 'ease-in-out', // CSS transition easing function

            // The "opener" function should return the element from which popup will be zoomed in
            // and to which popup will be scaled down
            // By defailt it looks for an image tag:
            opener: function(openerElement) {
                // openerElement is the element on which popup was initialized, in this case its <a> tag
                // you don't need to add "opener" option if this code matches your needs, it's defailt one.
                return openerElement.is('img') ? openerElement : openerElement.find('img');
            }
        }
    });

})(jQuery);

// Opening profile sidenav
function openProfNav(){
    document.getElementById("reservationnav").style.width = "0";
    document.getElementById("passnav").style.width = "0%";
    document.getElementById("profilenav").style.width = "60%";
}

// Opening change-password sidenav
function openPassNav(){
    document.getElementById("reservationnav").style.width = "0";
    document.getElementById("profilenav").style.width = "0%";
    document.getElementById("passnav").style.width = "60%";
}

// Opening reservations sidenav
function openReservationsNav(){
    document.getElementById("profilenav").style.width = "0%";
    document.getElementById("passnav").style.width = "0%";
    document.getElementById("reservationnav").style.width = "60%";
}

// opening the primary sidenav
function openNav() {
    document.getElementById("mySidenav").style.width = "20%";
}

/* Set the width of the side navigation to 0 */
function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("profilenav").style.width = "0%";
    document.getElementById("passnav").style.width = "0%";
    document.getElementById("reservationnav").style.width = "0";
}

function closeNavsByExit() {
    const allnavs = document.getElementsByClassName('detailedsidenav');
    for(var i = 0; i < allnavs.length; i++){
        allnavs[i].style.width = '0';
    }
}

$('#home').hover(function () {
    closeNavsByExit();
});
$('.nav').hover(function () {
    closeNavsByExit();
});


// SMOOTH SCROLL and CHANGE OF ACTIVE LINK
let lastId,
    topMenu = $("#top-menu"),
    topMenuHeight = topMenu.outerHeight() + 15,
    // All list items
    menuItems = topMenu.find("a"),
    // Anchors corresponding to menu items
    scrollItems = menuItems.map(function () {
        var item = $($(this).attr("href"));
        if (item.length) {
            return item;
        }
    });

// Bind click handler to menu items
// so we can get a fancy scroll animation
menuItems.click(function(e){
    const href = $(this).attr("href"),
        offsetTop = href === "#" ? 0 : $(href).offset().top - topMenuHeight + 1;
    $('html, body').stop().animate({
        scrollTop: offsetTop
    }, 800);
    e.preventDefault();
});

// Bind to scroll
$(window).scroll(function(){
    // Get container scroll position
    const fromTop = $(this).scrollTop() + topMenuHeight;

    // Get id of current scroll item
    let cur = scrollItems.map(function () {
        if ($(this).offset().top < fromTop)
            return this;
    });
    // Get the id of the current element
    cur = cur[cur.length-1];
    const id = cur && cur.length ? cur[0].id : "";

    if (lastId !== id) {
        lastId = id;
        // Set/remove active class
        menuItems
            .parent().removeClass("active")
            .end().filter("[href='#"+id+"']").parent().addClass("active");
    }
});



// UPDATING DESTINATIONS BASED ON THE SELECTED ORIGIN
function refresh_destinations(){
    // get value of the selected origin
    let option = document.getElementById('origin').value;
    // send an ajax request to get destinations
    $.ajax({
        method: "POST",
        url: "get-destinations",
        data: {
            'origin': option
        },
        success: function(data) {
            let  destinations = data['destinations'];
            let container = document.getElementById('destination');
            let banner = document.getElementById('booking-warning');
            let content = `<Option value="">Select</Option>`;
            if (destinations.length>0){
                for(let i=0;i<destinations.length;i++){
                    content += `<Option value="${destinations[i]}">${destinations[i]}</Option>`
                }

                banner.innerText = '';

            }else{
                banner.innerText = 'No destinations were found for the selected origin';

            }
            //update destination options
            container.innerHTML = content;
        }
    });
}

function check_seats(){
let origin = document.getElementById('origin').value;
let destination = document.getElementById('destination').value;
let time = document.getElementById('booking_time').value;
let date = document.getElementById('booking_date').value;
if (origin && destination && time && date){
    $.ajax({
        method: "POST",
        url: "check-seats",
        data: {
            'origin': origin,
            'destination':destination,
            'time':time,
            'date':date
        },
        success: function (data) {
          let message = data['message'];
          let code = data['code'];
          if (code !==0){
              let banner = document.getElementById('booking-warning');
              banner.innerHTML = message
          }else{
              let content1 = document.getElementById('booking-form-view');
              let content2 = document.getElementById('seats-view');
              content1.createAttribute('hidden');
              content2.removeAttribute('hidden');

          }
        }
    });

}else{
    let banner = document.getElementById('booking-warning');
    banner.innerHTML = 'Missing fields detected. Please ensure that all fields contains valid values';
}

}


function check_out(){
    if (selected_seats.size===0){
        alert('You have not selected any seat');
    }else{

    }
}


function setTimeSelector(){
        let container = document.getElementById('booking_time');
        let content = `<Option value="">Select</Option>`;
        for(let i=0;i<24;i++){
            if(i<10){
               content += `<Option value="0${i}:00">0${i}00hrs</Option>`;
            }else{
                content += `<Option value="${i}:00">${i}00hrs</Option>`;
            }
        }
        container.innerHTML = content;
    }

