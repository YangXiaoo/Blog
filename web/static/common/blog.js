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
            _this.html('回复').removeClass('btn-danger arc-reply');
            $('.guestbook_box').append(_form);
            _form.find('input[name="ruid"]').val(0);
            _form.find('input[name="pcid"]').val(-1);
        }else{   //回复
            $('.arc-btn').html('回复').removeClass('btn-danger arc-reply');   //其他按钮还原
            _this.html('取消回复').addClass('btn-danger arc-reply');
            var _item = _this.closest('.item');
            _this.after(_form);
            _form.find('input[name="ruid"]').val(_this.data('ruid'));
            _form.find('input[name="pcid"]').val(_this.data('pcid'));           
        }
    });
});