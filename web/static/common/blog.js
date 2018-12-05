$(function(){

    // toastr settings
    toastr.options = {
        closeButton: true,                  
        debug: false,                 
        progressBar: true,                
        positionClass: "toast-top-right",  
        showDuration: "300",                
        preventDuplicates: true,          
        hideDuration: "300",             
        timeOut: "3000",                
        extendedTimeOut: "1000",          
        showEasing: "swing",                
        hideEasing: "linear",        
        showMethod: "fadeIn",               
        hideMethod: "fadeOut"               
    };


    // tooltip
    $('[data-toggle="tooltip"]').tooltip();


   $('body').off('click', '.up-btn');
    $('body').on("click", '.up-btn', function(event){
        var _this_up_btn = $(this); 
        var up_url = _this_up_btn.data('url');
        BootstrapDialog.confirm({
            title: "上传 - Upload",
            message: '<form method="POST" action="'+up_url+'" enctype="multipart/form-data" ><input type="file" name="imgFile" class="Uploads" /></form>',
            btnCancelLabel: '取消',
            btnOKLabel: '确定',
            callback: function(result) {
                if(result) {
                    var form = $('.modal-dialog').find('form');
                    var ajax_option={
                        dataType:'json',
                        success:function(data){
                            if(data.success == '1'){
                                _this_up_btn.prev().attr("href", data.url);
                                _this_up_btn.prev().find('img').attr("src", data.url);
                                _this_up_btn.closest('.input-group').find('input').val(data.url);
                                $.amaran({'message':data.info});
                            }else{
                                $.amaran({'message':data.info});
                            }
                        }
                    }
                    form.ajaxSubmit(ajax_option);
                }
            }
        });
    });


    $('body').off('click', '.arc-thumbs');
    $('body').on("click", '.arc-thumbs', function(event){
        var _this = $(this);
        var id = _this.data('id');
        var kind = _this.data('kind');
        var url_path = _this.data('url')
        var dataStr = jQuery.parseJSON( '{"id":"'+id+'","kind":"'+kind+'"}' );

        var val = _this.find('span').text();
            val = parseInt(val)+1;
        _this.attr('disabled',"true");
        $.ajax({
            type : "get",
            url : url_path,
            dataType : 'json',
            data : dataStr,
            success : function(data) {
                if(data.status == '1'){
                    _this.find('span').text(val);
                    toastr.success(data.info);
                }else{
                    toastr.warning(data.info);
                }
                $(".tooltip.fade.top.in").remove();
            }
        });
    });

    $('body').off('click', '.arc-btn');
    $('body').on("click", '.arc-btn', function(event){
        var _this = $(this);
        var _form = $('.arc-form');
        if(_this.hasClass('arc-reply')){   //取消回复
            _this.html('回复');
            _this.find('i').removeClass('fa fa-remove');
            _this.find('i').addClass('fa fa-mail-reply');
            _this.removeClass('arc-reply')
            $('.guestbook_box').append(_form);
            _form.find('input[name="ruid"]').val(0);
            _form.find('input[name="pcid"]').val(-1);
        }else{   //回复
            _this.html('取消');
            _this.find('i').removeClass('fa fa-mail-reply');
            _this.find('i').addClass('fa fa-remove');
            _this.addClass('arc-reply')
            _this.after(_form);
            _form.find('input[name="ruid"]').val(_this.data('ruid'));
            _form.find('input[name="pcid"]').val(_this.data('pcid'));           
        }
    });

    $('body').off('click', '#new-load-btn');
    $('body').on("click", '#new-load-btn', function(event) {
        var _this = $(this);
        var page = _this.data('page');
        var id = _this.data('id');
        var url_path = _this.data('url');
        _this.button('loading');
        var dataStr = jQuery.parseJSON( '{"id":"'+id+'","page":"'+page+'"}' );
        $.ajax({
            type: "post",
            url: url_path,
            dataType : 'json',
            data: dataStr,
            success: function(data) {
                if (data.status == '1') {
                    $('.new-load-box').append(data.info);
                    _this.data("page", page + 1);
                    _this.button('reset');
                } else {
                    _this.text('emmm, 没啦');
                }
            }
        }); 
    });

    // nav bar scroll
    var new_scroll_position = 0;
    var last_scroll_position;
    var header = document.getElementById("nav-head");

    window.addEventListener('scroll', function(e) {
        last_scroll_position = window.scrollY;

        // Scrolling down
        if (new_scroll_position < last_scroll_position && last_scroll_position > 80) {
            // header.removeClass('slideDown').addClass('slideUp');
            header.classList.remove("slideDown");
            header.classList.add("slideUp");

        // Scrolling up
        } else if (new_scroll_position > last_scroll_position) {
            // header.removeClass('slideUp').addClass('slideDown');
            header.classList.remove("slideUp");
            header.classList.add("slideDown");
        }

        new_scroll_position = last_scroll_position;
    });

});