let selected_seats = new Set(), booking_data;

function display_seats(){
    let firstSeatLabel = 1;
    let f_cost = document.getElementById('f-cost').value;
    let e_cost = document.getElementById('e-cost').value;
    const $cart = $('#selected-seats'),
        $counter = $('#counter'),
        $total = $('#total'),
        sc = $('#seat-map').seatCharts({
            map: [
                'ff_ff',
                'ff_ff',
                '___ee',
                'ee_ee',
                'ee_ee',
                'ee_ee',
                'ee_ee',
                'eeeee',
            ],
            seats: {
                f: {
                    price: parseInt(f_cost),
                    classes: 'first-class', //your custom CSS class
                    category: 'First Class'
                },
                e: {
                    price: parseInt(e_cost),
                    classes: 'economy-class', //your custom CSS class
                    category: 'Economy Class'
                }

            },
            naming: {
                top: false,
                getLabel: function (character, row, column) {
                    return firstSeatLabel++;
                },
            },
            legend: {
                node: $('#legend'),
                items: [
                    ['f', 'available', 'First Class'],
                    ['e', 'available', 'Economy Class'],
                    ['f', 'unavailable', 'Already Booked']
                ]
            },
            click: function () {
                if (this.status() === 'available') {
                    //let's create a new <li> which we'll add to the cart items
                    $('<li>' + this.data().category + ' Seat # ' + this.settings.label + ': <b>KES' + this.data().price + '</b> <a href="#" class="cancel-cart-item">[cancel]</a></li>')
                        .attr('id', 'cart-item-' + this.settings.id)
                        .data('seatId', this.settings.id)
                        .appendTo($cart);

                    /*
                     * Lets update the counter and total
                     *
                     * .find function will not find the current seat, because it will change its stauts only after return
                     * 'selected'. This is why we have to add 1 to the length and the current seat price to the total.
                     */
                    $counter.text(sc.find('selected').length + 1);
                    $total.text(recalculateTotal(sc) + this.data().price);
                    // add seat to the set of selected seats
                    selected_seats.add(this.settings.label);
                    return 'selected';
                } else if (this.status() === 'selected') {
                    //update the counter
                    $counter.text(sc.find('selected').length - 1);
                    //and total
                    $total.text(recalculateTotal(sc) - this.data().price);

                    //remove the item from our cart
                    $('#cart-item-' + this.settings.id).remove();

                    //seat has been vacated
                    selected_seats.delete(this.settings.label);
                    console.log(selected_seats);
                    return 'available';
                } else if (this.status() === 'unavailable') {
                    //seat has been already booked
                    return 'unavailable';
                } else {
                    return this.style();
                }
            }
        });

    //this will handle "[cancel]" link clicks
    $('#selected-seats').on('click', '.cancel-cart-item', function () {
        //let's just trigger Click event on the appropriate seat, so we don't have to repeat the logic here
        sc.get($(this).parents('li:first').data('seatId')).click();
    });

    return sc
}

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

function openDetailedSideNav(x){
    let navs = document.getElementsByClassName('detailedsidenav');
    for(let i=0;i<navs.length;i++){
        navs[i].style.width = "0";
    }
    navs[x].style.width = "60%";
    toggleCarets(x);
}
function toggleCarets(x){
    let carets = document.getElementsByClassName('arrow');
    for(let i=0;i<carets.length;i++){
        if(i !== x){
           carets[i].classList.toggle('fa-angle-right');
        }else{
            carets[i].classList.toggle('fa-angle-left');
        }
    }
}



// opening the primary sidenav
function openPrimarySideNav() {
    document.getElementById("mySidenav").style.width = "20%";
}

/* Set the width of the side navigation to 0 */
function closeAll() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("profilenav").style.width = "0%";
    document.getElementById("passnav").style.width = "0%";
    document.getElementById("reservationnav").style.width = "0";
}

function closeNavsByExit() {
    const allnavs = document.getElementsByClassName('detailedsidenav');
    for(let i = 0; i < allnavs.length; i++){
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
        url: "get-destinations/",
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

// checking which seats are booked and which ones are not and painting them accordingly
function check_seats(){
    let origin = document.getElementById('origin').value;
    let destination = document.getElementById('destination').value;
    let time = document.getElementById('booking_time').value;
    let date = document.getElementById('booking_date').value;
    if (origin && destination && time && date){
        $.ajax({
            method: "POST",
            url: "check-seats/",
            data: {
                'origin': origin,
                'destination':destination,
                'time':time,
                'date':date
            },
            success: function (data) {
                let message = data['message'];
                if(message){
                    let banner = document.getElementById('booking-warning');
                    banner.innerHTML = message;
                }else{
                    let booked_seats = data['booked_seats'];
                    let cost1= data['first_class'], cost2= data['economy'];
                    let f_cost = document.getElementById('f-cost');
                    let e_cost = document.getElementById('e-cost');
                    f_cost.value = cost1;
                    e_cost.value = cost2;
                    let sc = display_seats();
                    console.log(sc.seats.price);
                    if (booked_seats.length !==0){
                        for(let i=0;i<booked_seats.length;i++){
                            booked_seats[i] = get_seat_id(booked_seats[i])
                        }
                        sc.get(booked_seats).status('unavailable');
                    }
                    // console.log(sc.seats);
                    let content1 = document.getElementById('booking-form-view');
                    let content2 = document.getElementById('seats-view');
                    content1.setAttribute('hidden','');
                    content2.removeAttribute('hidden');
                    booking_data = data;
                }

            }
        });

    }else{
        let banner = document.getElementById('booking-warning');
        banner.innerHTML = 'Missing fields detected. Please ensure that all fields contains valid values';
    }

}


function check_out(){
    if (selected_seats.size===0 ){
        alert('Please select a seat');
    }else{
        // if(booking_data){
        // let seats = get_seats_string(selected_seats);
        $.ajax({
            method: "POST",
            url: "",
            data: {
                'route_id': booking_data['route_id'],
                'datetime': booking_data['datetime'],
                'seats': get_seats_string(Array.from(selected_seats)),
                'amount': document.getElementById('total').innerHTML,
            },
            success: function (data) {
                let message = data['message'];
                if(message){
                    let banner = document.getElementById('booking-warning');
                    banner.innerHTML = message;
                }else{
                    let field, form;
                    field = document.getElementById('booking_id');
                    field.value = data['booking_id'];
                    form = document.getElementById('summary-view-form');
                    form.submit();
                }
            }
        });
    }
    // }
}

// Populate time_selector field with hourly time
function setTimeSelector(){
    let container = document.getElementById('booking_time');
    if (container){
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

}

// convert seat_num to seat_id
function get_seat_id(seat_num) {
    let num_of_seats = document.getElementsByClassName("seatCharts-seat").length-3;
    let row = 1, col = 1, count = 0;
    while (count < num_of_seats) {
        let current_seat = document.getElementById(row.toString().concat("_").concat(col.toString()));
        if (current_seat) {
            count += 1;
        }
        if (count === seat_num) {
            break;
        }
        if (col === 5) {
            col = 1;
            row += 1;
        } else {
            col += 1;
        }
    }
    if (count === seat_num) {
        return row.toString().concat("_").concat(col.toString());
    }else{
        console.log("Invalid seat number");
        return false
    }

}


function get_seats_string(set){
    console.log(set);
    let string = "";
    for(let i=0;i<set.length;i++){
        string = string.concat((set[i]).toString().concat(','))
    }
    console.log(string);
    return string
}