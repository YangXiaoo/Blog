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


    // 修改状态
    $('body').off('click', 'td a.editimg');
    $('body').on('click', 'td a.editimg', function(event){
        var addclass;
        var removeclass;
        var pvalue; 
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
        var dataStr = jQuery.parseJSON( '{"id":"'+id+'","'+field+'":"'+pvalue+'"}' );
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
                    $.amaran({'message':data.info});
                }else if(data.status == '2'){
                    restlogin(data.info);
                }else{
                    $.amaran({'message':data.info});
                }
            }
        });
    });


    // ajax修改名称
    $('.editable').editable({
        emptytext: "empty",
        params: function(params){
            var data = {};
            data['id'] = params.pk
            data['name'] = params.value
            return data;
        },
        success: function(response, newValue){
            var res = $.parseJSON(response);
            if (res.status == 1) {

            }else{
                return res.info;
            }
        }
    });


    // ajax处理数据
    $('body').off('click', '.edit_inline');
    $('body').on('click', '.edit_inline', function(event){
        var _this = $(this);
        var row = _this.closest('tr');
        var id = _this.data('id');
        var field = _this.data('field');
        var value = _this.data('value');
        var url = _this.data('url');
        var title = _this.data('title');
        var content = _this.data('content');
        var dataStr = jQuery.parseJSON( '{"id":"'+id+'","'+field+'":"'+value+'"}' );
        BootstrapDialog.confirm({
            title: title,
            message: content,
            btnCancelLabel: '取消',
            btnOKLabel: '确定',
            callback: function(result) {
                if(result) {
                    $.ajax({
                        type : "post",
                        url : url,
                        dataType : 'json',
                        data : dataStr,
                        success : function(data) {
                            if(data.status == '1'){
                                $.amaran({'message':data.info});
                            }else{
                                $.amaran({'message':data.info});
                            }
                        }
                    });
                }
            }
        });
    });


    //Initialize Select2 Elements
    $('.select2').select2()

    //Date range picker
    $('#reservation').daterangepicker()
    //Date range picker with time picker
    $('#reservationtime').daterangepicker({ timePicker: true, timePickerIncrement: 30, format: 'MM/DD/YYYY h:mm A' })
    //Date range as a button
    $('#daterange-btn').daterangepicker(
      {
        ranges   : {
          'Today'       : [moment(), moment()],
          'Yesterday'   : [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
          'Last 7 Days' : [moment().subtract(6, 'days'), moment()],
          'Last 30 Days': [moment().subtract(29, 'days'), moment()],
          'This Month'  : [moment().startOf('month'), moment().endOf('month')],
          'Last Month'  : [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        },
        startDate: moment().subtract(29, 'days'),
        endDate  : moment()
      },
      function (start, end) {
        $('#daterange-btn span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'))
      }
    )

    //Date picker
    $('#datepicker').datepicker({
      autoclose: true,
      format: 'YYYY-MM-DD',
    })

    //iCheck for checkbox and radio inputs
    $('input[type="checkbox"].minimal, input[type="radio"].minimal').iCheck({
      checkboxClass: 'icheckbox_minimal-blue',
      radioClass   : 'iradio_minimal-blue'
    })
    //Red color scheme for iCheck
    $('input[type="checkbox"].minimal-red, input[type="radio"].minimal-red').iCheck({
      checkboxClass: 'icheckbox_minimal-red',
      radioClass   : 'iradio_minimal-red'
    })
    //Flat red color scheme for iCheck
    $('input[type="checkbox"].flat-red, input[type="radio"].flat-red').iCheck({
      checkboxClass: 'icheckbox_flat-green',
      radioClass   : 'iradio_flat-green'
    })

    //Colorpicker
    $('.my-colorpicker1').colorpicker()
    //color picker with addon
    $('.my-colorpicker2').colorpicker()
/*    //Timepicker
    $('.timepicker').timepicker({
      showInputs: false
    })*/

    // 跳转链接
    $('input[type="checkbox"][value="j"]').on('ifChecked', function(event){
        $("#jumplink").removeClass("hide");
    });
    $('input[type="checkbox"][value="j"]').on('ifUnchecked', function(event){
        $("#jumplink").addClass("hide");
    });


    // 缩略图
    $('input[type="checkbox"][value="p"]').on('ifChecked', function(event){
        $("#litpic").removeClass("hide");
    });
    $('input[type="checkbox"][value="p"]').on('ifUnchecked', function(event){
        $("#litpic").addClass("hide");
    });


    // select all
    $('.checkbox-toggle').on('ifChecked', function(event){
        var _this = $(this);
        var _table = _this.closest('.table');
        _table.find("tr td input[type='checkbox']").iCheck("check");
    });
    $('.checkbox-toggle').on('ifUnchecked', function(event){
        var _this = $(this);
        var _table = _this.closest('.table');
        _table.find("tr td input[type='checkbox']").iCheck("uncheck");
    });



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



   $('body').off('click', '.upload-file');
    $('body').on("click", '.upload-file', function(event){
        var _this_up_btn = $(this); 
        var up_url = _this_up_btn.data('url');
        BootstrapDialog.confirm({
            title: "上传 - Upload",
            message: '<form method="POST" action="'+up_url+'" enctype="multipart/form-data" ><input type="file" name="file" class="Uploads" /></form>',
            btnCancelLabel: '取消',
            btnOKLabel: '确定',
            callback: function(result) {
                if(result) {
                    var form = $('.modal-dialog').find('form');
                    var ajax_option={
                        dataType:'json',
                        success:function(data){
                            if(data.success == '1'){
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
                        $.amaran({'message':data.info});
                    }else{
                         $.amaran({'message':data.info});
                    }
                }
            }
            form.ajaxSubmit(ajax_option);
        }
    });


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
                                    $.amaran({'message':data.info});
                                    $(table_box).each(function(){
                                        if(true == $(this).is(':checked')){
                                            $(this).closest('tr').remove();
                                        }
                                    });
                                    if (_this.hasClass('delete-one')){
                                        _this.closest('tr').remove();
                                    }
                                }else{
                                    $.amaran({'message':data.info});
                                }
                            }
                        });
                    }
                }
            });
        }
    });




});
