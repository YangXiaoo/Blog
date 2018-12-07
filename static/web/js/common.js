$(function(){
    $.pjax.defaults.timeout = 5000;
    $.pjax.defaults.maxCacheLength = 0;
    
    toastr.options = {
        closeButton: true,                  //鏄惁鏄剧ず鍏抽棴鎸夐挳
        debug: false,                       //鏄惁浣跨敤debug妯″紡
        progressBar: true,                  //鏄惁鏄剧ず杩涘害鏉�
        positionClass: "toast-top-right",   //寮瑰嚭绐楃殑浣嶇疆
        showDuration: "300",                //鏄剧ず鍔ㄤ綔鏃堕棿
        preventDuplicates: true,            //鎻愮ず妗嗗彧鍑虹幇涓€娆�
        hideDuration: "300",                //闅愯棌鍔ㄤ綔鏃堕棿
        timeOut: "3000",                    //鑷姩鍏抽棴瓒呮椂鏃堕棿
        extendedTimeOut: "1000",            ////鍔犻暱灞曠ず鏃堕棿
        showEasing: "swing",                //鏄剧ず鏃剁殑鍔ㄧ敾缂撳啿鏂瑰紡
        hideEasing: "linear",               //娑堝け鏃剁殑鍔ㄧ敾缂撳啿鏂瑰紡
        showMethod: "fadeIn",               //鏄剧ず鏃剁殑鍔ㄧ敾鏂瑰紡
        hideMethod: "fadeOut"               //娑堝け鏃剁殑鍔ㄧ敾鏂瑰紡
    };
    
    //閫€鍑虹櫥褰�
    $('body').off('click', '.login_out');
    $('body').on("click", '.login_out', function(event){
        var url = $(this).attr('href');
        window.location.href=url;
        return false;
    });

    
    $(document).pjax('a:not(a[target="_blank"])', {container:'#pjax-container', fragment:'#pjax-container'});
    
    $(document).on('submit', 'form[pjax-search]', function(event) {
        var _this = $(this);
        $.pjax.submit(event, {container:'#pjax-container', fragment:'#pjax-container'});
        _this.find('input[name="k"]').val('');
    })
    
    $(document).on('pjax:send', function() { NProgress.start(); });
    $(document).on('pjax:complete', function() { NProgress.done(); });
    
    //鎻愪氦
    $('body').off('click', '.submits');
    $('body').on("click", '.submits', function(event){
        var _this = $(this);
        _this.button('loading');
        var form = _this.closest('form');
        if(form.length){
            var ajax_option={
                dataType:'json',
                success:function(data){
                    if(data.status == '1'){
                        toastr.success(data.info);
                        var url = data.url;
                        $.pjax({url: url, container: '#pjax-container', fragment:'#pjax-container'})
                    }else{
                        _this.button('reset');
                        toastr.warning(data.info);
                    }
                }
            }
            form.ajaxSubmit(ajax_option);
        }
    });
    
    //denglu
    $('body').off('click', '.login-btn');
    $('body').on("click", '.login-btn', function(event){
        var _this = $(this);
        _this.button('loading');
        var form = _this.closest('form');
        if(form.length){
            var ajax_option={
                dataType:'json',
                success:function(data){
                    if(data.status == '1'){
                        toastr.success(data.info);
                        var url = data.url;
                        window.location.href=url;
                    }else{
                        _this.button('reset');
                        $('#code').click();
                        toastr.warning(data.info);
                    }
                }
            }
            form.ajaxSubmit(ajax_option);
        }
    });
/**
 * @todo   点赞
 */
    $('body').off('click', '.arc-thumbs-up');
    $('body').on("click", '.arc-thumbs-up', function(event){
        var _this = $(this);
        var id = _this.data('id');
        var kind = _this.data('kind');
        if (kind == 0) {
            var url_path = '/Tp5/public/index/detail/thumb/id/';
        }else{
            var url_path = '/Tp5/public/index/userdetail/thumb/id/';
        }
        var val = _this.find('span').text();
            val = parseInt(val)+1;
        _this.attr('disabled',"true");
        $.ajax({
            type : "get",
            url : url_path+id,
            dataType : 'json',
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
/**
 * @todo  回复消息按钮
 */
    $('body').off('click', '.arc-btn');
    $('body').on("click", '.arc-btn', function(event){
        var _this = $(this);
        var _form = $('.arc-form');
        if(_this.hasClass('arc-reply')){   //取消回复
            _this.html('回复').removeClass('btn-danger arc-reply');
            $('.guestbook_box').append(_form);
            _form.find('input[name="ruid"]').val(0);
            _form.find('input[name="cid"]').val(0);
        }else{   //回复
            $('.arc-btn').html('回复').removeClass('btn-danger arc-reply');   //其他按钮还原
            _this.html('取消回复').addClass('btn-danger arc-reply');
            var _item = _this.closest('.item');
            _this.after(_form);
            _form.find('input[name="ruid"]').val(_this.data('uid'));
            _form.find('input[name="cid"]').val(_this.data('cid'));
            _form.find('input[name="tid"]').val(_this.data('tid'));            
        }
    });
/**
 * @todo  关注好友
 */
    $('body').off('click', '.follow');
    $('body').on('click', '.follow', function(event){
        var _this = $(this);
        var id = _this.data('fid');
        _this.attr('disabled', "true");
        $.ajax({
            type : "get",
            url : '/Tp5/public/index/profile/follow/id/'+id,
            dataType : 'json',
            success : function(data){
                if (data.status == '1'){
                    toastr.success(data.info); 
                }else{
                    toastr.warning(data.info);
                }
            }
        });
    });
/**
 *@todo  收藏文章
 *@time(2018-3-8)
 */
    $('body').off('click', '#collect');
    $('body').on('click', '#collect', function(event){
        var _this = $(this);
        var aid = _this.data('aid');
        var id = _this.data('id');
        if (id == 0) {
            var url_path = '/Tp5/public/index/detail/like/aid/';
        }else{
            var url_path = '/Tp5/public/index/userdetail/like/aid/';
        }
        _this.attr('disabled', "true");
        $.ajax({
            type : "get",
            url : url_path+aid,
            dataType : 'json',
            success : function(data){
                if (data.status == '1') {
                    toastr.success(data.info);
                    _this.find('i').addClass('bg-red');
                    var val = _this.find('span').text();
                    val = parseInt(val)+1;
                    _this.find('span').text(val); 
                }else if(data.status == '0'){
                    toastr.warning(data.info);
                    _this.find('i').addClass('bg-red');
                    var val = _this.find('span').text();
                }else{
                    toastr.warning(data.info);
                    $('#plzlog').click();
                }
            }
        });
    });
    


    //单条删除-批量删除
    $('body').off('click', '.delete-one,.delete-all');
    $('body').on("click", '.delete-one,.delete-all', function(event){
        event.preventDefault();
        var _this = $(this);
        var title = _this.data('title')?_this.data('title'):'删除';
        var url_del = _this.data('url')||'';
        var message = _this.data('message')?_this.data('message'):'确认操作？';
        if(_this.hasClass('delete-all')){   //批量删除
            var id = '';
            var str = '';
            var table_box = _this.closest('.box-header').next('.box-body').find(".table tr td input[name='id[]']");
            $(table_box).each(function(){
                if(true == $(this).is(':checked')){
                    str += $(this).val() + ",";
                }
            });
            if(str.substr(str.length-1)== ','){
                id = str.substr(0, str.length-1);
            }
        }else{                              //单条删除
            var id = _this.data('id')||'';
        }
        if(id && url_del){
            BootstrapDialog.confirm({
                onshow:function(obj){
                    var cssConf = {};
                    cssConf['width']=300;
                    if(cssConf){
                        obj.getModal().find('div.modal-dialog').css(cssConf);
                    }
                },
                title: title,
                message: message,
                btnCancelLabel: '取消',
                btnOKLabel: '确定',
                callback: function(resultDel) {
                    if(resultDel === true) {
                        $.ajax({
                            type : "post",
                            url : url_del,
                            dataType : 'json',
                            data : { id:id, },
                            success : function(data) {
                                if(data.status == '1'){
                                    toastr.success(data.info);
                                    var url = data.url;
                                    $.pjax({url: url, container: '#pjax-container', fragment:'#pjax-container'})
                                }else if(data.status == '2'){
                                    restlogin(data.info);
                                }else{
                                    toastr.warning(data.info);
                                }
                            }
                        });
                    }
                }
            });
        }
    });
    
   $('body').off('click', '.up-btn');
    $('body').on("click", '.up-btn', function(event){
        var _this_up_btn = $(this);   //当前上传按钮
        var up_url = _this_up_btn.data('url');   //上传地址
        //var $('.modal-dialog .Uploads').val();
        
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
                            if(data.error == '0'){
                                _this_up_btn.prev().attr("href", data.url);
                                _this_up_btn.prev().find('img').attr("src", data.url);
                                _this_up_btn.closest('.input-group').find('input').val(data.url);
                                toastr.success(data.info);
                            }else{
                                toastr.warning(data.info);
                            }
                        }
                    }
                    form.ajaxSubmit(ajax_option);
                }
            }
        });
    });
    
    //状态status列表修改（只能进行0和1值的切换）
    $('body').off('click', 'td a.editimg');
    $('body').on('click', 'td a.editimg', function(event){
        var addclass;
        var removeclass;
        var pvalue;   //提交值
        var _this = $(this);
        var field = _this.data('field');
        var id = _this.data('id');
        var value = _this.data('value');
        var url = _this.data('url');
        if ( value == 1){
            pvalue = 0;
            addclass = "fa-check-circle text-green";
            removeclass = "fa-times-circle text-red";
        }else{
            pvalue = 1;
            addclass = "fa-times-circle text-red";
            removeclass = "fa-check-circle text-green";
        }
        var dataStr = jQuery.parseJSON( '{"id":"'+id+'","'+field+'":"'+pvalue+'"}' );   //字符串转json
        $.ajax({
            type : "post",
            url : url,
            dataType : 'json',
            data : dataStr,
            success : function(data) {
                if(data.status == '1'){
                    _this.data('value', pvalue);
                    _this.removeClass(addclass);
                    _this.addClass(removeclass);
                    toastr.success(data.info);
                }else if(data.status == '2'){
                    restlogin(data.info);
                }else{
                   toastr.success(data.info);
                }
            }
        });
    });
  $('[data-toggle="tooltip"]').tooltip();
})
    
$(window).scroll(function(){
    var sc=$(window).scrollTop();
    var rwidth=$(window).width()+$(document).scrollLeft();
    var rheight=$(window).height()+$(document).scrollTop();
    if(sc>0){
        $("#goTop").css("display","block");
    }else{
        $("#goTop").css("display","none");
    }
});

/*杩斿洖椤堕儴*/

/*鎵嬫満鍥哄畾*/
$(window).resize(function(){
    if($(window).width() < 500){
        $('body').removeClass("layout-boxed").addClass("fixed");
    }
});
if($(window).width() < 500){
    $('body').removeClass("layout-boxed").addClass("fixed");
}
/*鎵嬫満鍥哄畾*/
