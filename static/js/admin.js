/**
 * Admin-specific JavaScript functionality
 */

// Document ready function to initialize admin components
$(document).ready(function() {
    console.log("Admin JS loaded");
    
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Initialize popovers
    $('[data-bs-toggle="popover"]').popover();
    
    // Confirm before deleting
    $('.confirm-delete').on('click', function() {
        return confirm('Are you sure you want to delete this item? This action cannot be undone.');
    });
    
    // Toggle sidebar
    $('#sidebarToggle').on('click', function() {
        $('body').toggleClass('sidebar-toggled');
        $('.sidebar').toggleClass('toggled');
        
        if ($('.sidebar').hasClass('toggled')) {
            $('.sidebar .collapse').collapse('hide');
        }
    });
    
    // Close any open menu accordions when window is resized below 768px
    $(window).resize(function() {
        if ($(window).width() < 768) {
            $('.sidebar .collapse').collapse('hide');
        }
    });
    
    // Prevent the content wrapper from scrolling when the fixed side navigation is hovered over
    $('body.fixed-nav .sidebar').on('mousewheel DOMMouseScroll wheel', function(e) {
        if ($(window).width() > 768) {
            const e0 = e.originalEvent,
                delta = e0.wheelDelta || -e0.detail;
            this.scrollTop += (delta < 0 ? 1 : -1) * 30;
            e.preventDefault();
        }
    });
    
    // Scroll to top button appear
    $(document).on('scroll', function() {
        const scrollDistance = $(this).scrollTop();
        if (scrollDistance > 100) {
            $('.scroll-to-top').fadeIn();
        } else {
            $('.scroll-to-top').fadeOut();
        }
    });
    
    // Smooth scrolling using jQuery easing
    $(document).on('click', 'a.scroll-to-top', function(e) {
        const $anchor = $(this);
        $('html, body').stop().animate({
            scrollTop: ($($anchor.attr('href')).offset().top)
        }, 1000, 'easeInOutExpo');
        e.preventDefault();
    });
    
    // Initialize DataTables with common settings
    if ($.fn.DataTable) {
        $('.datatable').DataTable({
            responsive: true,
            stateSave: true,
            pageLength: 25,
            lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]]
        });
    }
    
    // Handle form submissions with loading state
    $('form.ajax-form').on('submit', function() {
        const $form = $(this);
        const $submitBtn = $form.find('button[type="submit"]');
        
        // Disable submit button and show loading state
        $submitBtn.prop('disabled', true).html(
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...'
        );
        
        // You can add AJAX form submission logic here if needed
        // For now, just re-enable the button after 3 seconds as an example
        setTimeout(function() {
            $submitBtn.prop('disabled', false).html('Submit');
        }, 3000);
        
        // Return true to submit the form normally
        return true;
    });
});
